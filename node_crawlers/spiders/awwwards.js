const Promise = require('bluebird');
const requestPromise = require('request-promise');
const cheerio = require('cheerio');
const Bottleneck = require('bottleneck');
const mongoUtil = require('../db');
var client;
var updateItem;

mongoUtil.connectToServer(function(err) {
    // start the rest of your app here
    client = mongoUtil.getClient();
    updateItem = mongoUtil.updateItem;
    if (err) {
        console.log(err);
    } else {
        start();
    }
});

const limiter = new Bottleneck({
    maxConcurrent: 10
});

const prefix = 'https://www.awwwards.com';

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
    console.info(`Starting Awwwards spider`);
    const url = prefix + '/directory/?page=1';
    limiter.schedule({priority: 2}, requestPromise, getOptions(url))
        .then(($) => {
            parseDirectory($, url);
        });
}

function parseDirectory($, directoryUrl) {
    let promises = [];
    console.info(`Scheduling directory: ${directoryUrl}`);
    $('.box-item .profile-link').each(function(index,element) { 
        let profileUrl = prefix + $(this).attr('href');
        console.info(`Scheduling profile: ${profileUrl}`);
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

            let projects = [];
            $('.grid ul.list-items div.box-item').each(function(index,element){
                let recognitions = null;
                $(this).find('.list-tags > li .tooltip-text').each(function(index,element) {
                    if (!recognitions) recognitions = [];
                    recognitions.push($(this).text().trim());
                })
                projects.push({
                    name: $(this).find('.content h3 a').text().trim(),
                    url: prefix + $(this).find('.content h3 a').attr('href'),
                    likes: $(this).find('.rollover .js-collect-like .number').text().trim(),
                    from: $(this).find('.content .box-left').text().trim(),
                    date: $(this).find('.content .box-right').text().trim(),
                    recognitions,
                });
            });

            let awards = []; 
            let awardsUrl = $('.bt-laurel').attr('href');
            if (awardsUrl){
                promises.push(limiter.schedule({priority: 0}, requestPromise, getOptions(prefix + awardsUrl)).then(function($) {
                    console.info(`Parsing: ${prefix + awardsUrl}`);
                    $('.box-item').each(function (i,e) {
                        let recognitions = null;
                        $(this).find('.list-tags > li .tooltip-text').each(function(index,element) {
                            if (!recognitions) recognitions = [];
                            recognitions.push($(this).text().trim());
                        })
                        awards.push({
                            title: $(this).find('.content h3 a').text().trim(),
                            url: prefix + $(this).find('.content h3 a').attr('href'),
                            likes: $(this).find('.rollover .js-collect-like .number').text().trim(),
                            from: $(this).find('.content .box-left').text().trim(),
                            date: $(this).find('.content .box-right').text().trim(),
                            recognitions,
                        });
                    });
                }));
                
            }
            
            let jobs = [];
            let jobsUrl = $('.box-heading a[href$="jobs"]').attr('href');
            if(jobsUrl){
                promises.push(limiter.schedule({priority: 0}, requestPromise, getOptions(prefix + jobsUrl)).then(function($){
                    console.info(`Parsing: ${prefix + jobsUrl}`);
                    $('.box-item').each(function (i,e) {
                        jobs.push({
                            jobUrl: prefix + $(this).find('.box-info > a').attr('href'),
                            name: $(this).find('.box-rows .row:nth-of-type(2)').text().trim(),
                            location: $(this).find('.box-rows .row:nth-of-type(1)').text().trim(),
                            description: $(this).find('.box-rows .row:nth-of-type(4)').text().trim(),
                            field: $(this).find('.footer .box-left').text().trim(),
                            posted: $(this).find('.footer .box-right').text().trim()
                        })
                    });
                }));
            }
            let favorites = [];
            let favoritesUrl = $('.box-heading a[href$="favorites"]').attr('href');
            if(favoritesUrl){
                promises.push(limiter.schedule({priority: 0}, requestPromise, getOptions(prefix + favoritesUrl)).then(function($){
                    console.info(`Parsing: ${prefix + favoritesUrl}`);
                    $('.box-item').each(function (i,e) {
                        favorites.push({
                            favoriteUrl: prefix + $(this).find('.box-info .content .row:nth-of-type(1) h3 a').attr('href'),
                            name: $(this).find('.box-info .content .row:nth-of-type(1) h3').text().trim(),
                            from: $(this).find('.box-info .content .row:nth-of-type(2) .box-left').text().trim(),
                            posted: $(this).find('.box-info .content .row:nth-of-type(2) .box-right').text().trim()
                        })
                    });
                }));
            }

            let collections = [];
            let collectionsUrl = $('.box-heading a[href$="collections/"]').attr('href');
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
            
            let votes = [];
            let votesUrl = $('.box-heading a[href$="votes"]').attr('href');
            if(votesUrl){
                promises.push(limiter.schedule({priority: 0}, requestPromise, getOptions(prefix + votesUrl)).then(function($){
                    console.info(`Parsing: ${prefix + votesUrl}`);
                    $('.box-item').each(function (i,e) {
                        votes.push({
                            site: $(this).find('.content h3 a').text(),
                            url: prefix + $(this).find('.content h3 a').attr('href'),
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
                        projects,
                        awards,
                        jobs,
                        favorites,
                        collections,
                        votes
                    };
                    // delete unused properties
                    if (!obj.facebook) delete obj.facebook;
                    if (!obj.twitter) delete obj.twitter;
                    if (!obj.linkedin) delete obj.linkedin;
                    if (obj.awards === undefined || obj.awards.length == 0) {
                        delete obj.awards;
                    }
                    if (obj.projects === undefined || obj.projects.length == 0) {
                        delete obj.projects;
                    }
                    if (obj.jobs === undefined || obj.jobs.length == 0) {
                        delete obj.jobs;
                    }
                    if (obj.favorites === undefined || obj.favorites.length == 0) {
                        delete obj.favorites;
                    }
                    if (obj.collections === undefined || obj.collections.length == 0) {
                        delete obj.collections;
                    }
                    if (obj.votes === undefined || obj.votes.length == 0) {
                        delete obj.votes;
                    }
                    // mongo db upsert
                    updateItem(obj);
                })
                .catch(err => {
                    console.log(err);
                });
        }));
    });
    Promise.all(promises)
        .then(() => {
            // recursively follow next page
            let url = prefix + $('div.paginate > div span.current').next().attr('href');
            if(url){
                limiter.schedule({priority: 1}, requestPromise, getOptions(url))
                    .then(($) => {
                        parseDirectory($, url);
                    });
            }
        })
        .catch(err => {
            // catch error
            console.log(err);
            // recursively follow next page
            let url = prefix + $('div.paginate > div span.current').next().attr('href');
            if(url){
                limiter.schedule({priority: 1}, requestPromise, getOptions(url))
                    .then(($) => {
                        parseDirectory($, url);
                    });
            }
        });
}