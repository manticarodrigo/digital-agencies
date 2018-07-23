const fs = require('fs');
const Promise = require('bluebird');
const requestPromise = require('request-promise');
const cheerio = require('cheerio');
const Bottleneck = require('bottleneck');
const mongoUtil = require('../db');
var client;
var updateItem;

mongoUtil.connectToServer(function(err) {
    client = mongoUtil.getClient();
    updateItem = mongoUtil.updateItem;
    // start the rest of your app here
    if (err) console.log(err);
    start();
});

const limiter = new Bottleneck({
    maxConcurrent: 10
});

function getOptions(url){ 
    return {
        uri: url,
        //proxy: 'http://localhost:8888',
        //rejectUnauthorized: false,
        headers: {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'},
        transform: function (body) {
          return cheerio.load(body);
        }
    };
}

function start() {
    let totalpages = 111;
    let prefix = 'https://www.awwwards.com';
    let metadata = [];
    let promises = [];
    console.info(`Starting Awwwards spider, with ${totalpages} pages`);
    for (let i = 1; i < totalpages; i++) {
        let directoryUrl = prefix + '/directory/?page=' + i;
        promises.push(limiter.schedule({priority: 2}, requestPromise, getOptions(directoryUrl)).then(($) => {
            let promises = [];
            console.info(`Scheduling: ${directoryUrl}`);
            $('.box-item .profile-link').each(function(index,element) { 
                let profileUrl = prefix + $(this).attr('href');
                console.info(`Scheduling: ${profileUrl}`);
                promises.push(limiter.schedule({priority: 1}, requestPromise, getOptions(profileUrl)).then(function($) {
                    console.info(`Parsing: ${profileUrl}`);
                    let promises = [Promise.resolve()];
                    let source = profileUrl;
                    let provider = 'awwwards_partners';
                    let name = $('.box-profile .box-center .heading-medium').text().trim();
                    let websiteUrl = $('h1.heading-medium a').attr('href');
                    let countrycity = $('span.text-gray').text();
                    let shortDescription =  $('div.box-profile h2').text();
                    let fb = $('ul.list-bts').find('.bt-facebook').attr('href');
                    let twitter = $('ul.list-bts').find('.bt-twitter').attr('href');
                    let linkedin = $('ul.list-bts').find('.bt-linkedin').attr('href');

                    let awards = {
                        total : $('.bt-laurel .borders').text().trim(),
                        categories : []
                    }; 
                    let awardsUrl = $('.bt-laurel').attr('href');
                    if (awardsUrl){
                        promises.push(limiter.schedule({priority: 0}, requestPromise, getOptions(prefix + awardsUrl)).then(function($) {
                            console.info(`Parsing: ${prefix + awardsUrl}`);
                            let awardList = $('ul.js-tab-awards li[data-type]');
                            for (let i = 0; i < awardList.length; i++) {
                                const element = awardList.eq(i);
                                let type = element.data('type');
                                let count = $('.list-tags li.' + type).length;
                                awards.categories.push({type,count})
                            }
                            $ = null;
                        }));
                        
                    }

                    let projects = [];
                    $('.grid ul.list-items div.box-item').each(function(index,element){
                        projects.push({
                            name: $(this).find('.content h3 a').text().trim(),
                            url: $(this).find('.content h3 a').attr('href'),
                            date: $(this).find('.content .box-right').text().trim()
                        });
                    });

                    let showMeMore = $('a.item.more').attr('href');
                    if(showMeMore){
                        recursiveShowMeMore(showMeMore);
                    }

                    function recursiveShowMeMore(url){
                        console.info(`Parsing: ${prefix + url}`);
                        promises.push(limiter.schedule({priority: 0}, requestPromise, getOptions(prefix + url)).then(function($){
                            $('.grid ul.list-items div.box-item').each(function(index,element){
                                projects.push({
                                    name: $(this).find('.content h3 a').text().trim(),
                                    url: $(this).find('.content h3 a').attr('href'),
                                    date: $(this).find('.content .box-right').text().trim()
                                });
                            });
                            let showMeMore = $('a.item.more').attr('href');
                            if(showMeMore){
                                recursiveShowMeMore(showMeMore);
                            }
                        }));
                    }

                    let jobsUrl = $('.box-heading a[href$="jobs"]').attr('href');
                    let collectionsUrl = $('.box-heading a[href$="collections/"]').attr('href');
                    let votesUrl = $('.box-heading a[href$="votes"]').attr('href');
                    let collections = [];
                    let votes = [];
                    let jobs = [];
                    if(jobsUrl){
                        //???
                    }
                    if(collectionsUrl){
                        promises.push(limiter.schedule({priority: 0}, requestPromise, getOptions(prefix + collectionsUrl)).then(function($){
                            console.info(`Parsing: ${prefix + collectionsUrl}`);
                            $('.box-item').each(function (i,e) {
                                collections.push({
                                    name: $(this).find('.content h3 a').text().trim(),
                                    collectionUrl: $(this).find('.content h3 a').attr('href'),
                                    count: $(this).find('.text-gray').text(),
                                    curator:{
                                        name: $(this).find('.row-auto strong a').text().trim(),
                                        url: $(this).find('.row-auto strong a').attr('href')
                                    },
                                    followers: $(this).find('.box-users-likes .container-bt-circle span.number').text().trim()
                                })
                            });
                        }));
                    }
                    if(votesUrl){
                        promises.push(limiter.schedule({priority: 0}, requestPromise, getOptions(prefix + votesUrl)).then(function($){
                            console.info(`Parsing: ${prefix + votesUrl}`);
                            $('.box-item').each(function (i,e) {
                                votes.push({
                                    site: $(this).find('.content h3 a').text(),
                                    url: $(this).find('.content h3 a').attr('href'),
                                    date: $(this).find('.content .box-right').text().trim(),
                                    score: $(this).find('figure.rollover.darken div.note').text(),
                                    byUser: $(this).find('div.js-user').data('username'),
                                })
                            });
                        }));
                    }
                    
                    return Promise.all(promises)
                        .then(function(){
                            let obj = {
                                name,
                                source,
                                provider,
                                websiteUrl,
                                countrycity,
                                shortDescription,
                                fb,
                                twitter,
                                linkedin,
                                awards,
                                projects,
                                jobs,
                                collections,
                                votes
                            };
                            if (obj.awards === undefined || obj.awards.length == 0) {
                                delete obj.awards;
                            }
                            if (obj.projects === undefined || obj.projects.length == 0) {
                                delete obj.projects;
                            }
                            if (obj.jobs === undefined || obj.jobs.length == 0) {
                                delete obj.jobs;
                            }
                            if (obj.collections === undefined || obj.collections.length == 0) {
                                delete obj.collections;
                            }
                            if (obj.votes === undefined || obj.votes.length == 0) {
                                delete obj.votes;
                            }
                            metadata.push(obj);
                            // mongo db upsert
                            updateItem(obj);
                        })
                        .catch(err => {
                            console.log(err);
                        });
                }));
            });
            return Promise.all(promises);
        }));
    }

    Promise.all(promises)
        .catch(function(err) {
            // log that I have an error, return the entire array;
            console.error('A promise failed to resolve', err);
            return promises;
        })
        .then(function () {
            // Close mongodb
            client.close();
            // Write to file
            fs.writeFile('results.json', JSON.stringify(metadata, null, 4), function(error) {
                if (!error) {
                    console.log('JSON file successfully written.')
                } else{
                    console.error('Error while writing file' + error);
                }
            });
        });
    }