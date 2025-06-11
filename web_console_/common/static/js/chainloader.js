"use strict";

/**
*   Simple class for scheduling concurrent jobs.
*
*   The basic premise is that requests are scheduled into a queue,
*   and jobs only started when prior jobs have completed, with up to
*   <code>numConcurrentJobs</code> (default: 1) job(s) in progress at any
*   one time, with an optional <code>delay</code> (default: 0) millsecs
*   between jobs.
*
*   Example usage:
*
*       var loader = new ChainLoader( { numConcurrentJobs: 3, delay: 500 } );
*       for (var i = 1; i <= 10; i++ )
*       {
*           loader.schedule(
*               "job_" + i,
*               function() { console.log( "job done" ); loader.loadNext(); }
*           );
*       }
*       loader.load();
*
*   See also <code>ChainLoader.Image</code>.
*/
var ChainLoader = function( /*Map*/ options )
{
	this.jobs = {};
	this.jobQueue = [];
	this.jobsPending = {};
	this.numJobsRunning = 0;

	var opts = this.options =
		this._merge( {}, ChainLoader.defaultOptions, options || {} );
};


ChainLoader.defaultOptions = {
	numConcurrentJobs: 1,
	delay: 0,
	debug: 0,
};


ChainLoader.prototype._merge = function( target )
{
	for (var i in arguments)
	{
		for (var k in arguments[ i ])
		{
			target[ k ] = arguments[ i ][ k ];
		}
	}
	return target;
};


ChainLoader.prototype.schedule = function( jobId, jobFunc, jobOptions )
{
	if (!jobId) throw new Error( "Null jobId argument" );

	this.jobQueue.push( jobId );
	jobOptions = this._merge( {}, this.options, jobOptions || {} );

	this.jobs[ jobId ] = {
		jobFunc: jobFunc,
		options: jobOptions,
	};
};


ChainLoader.prototype.unschedule = function( jobId )
{
	var timerId = this.jobsPending[ jobId ];
	if (timerId)
	{
		clearTimeout( timerId );
		delete this.jobsPending[ jobId ];
	}
	this.jobQueue.remove( jobId );
	delete this.jobs[ jobId ];
};


ChainLoader.prototype.getJobs = function( numJobs )
{
    return this.jobQueue.splice( 0, numJobs );
};


ChainLoader.prototype.load = function()
{
	var maxJobs = this.options.numConcurrentJobs || 1;
	var numJobs = maxJobs - this.numJobsRunning;
	if (this.isFinished())
	{
		// this.log( "no jobs left" );
		return;
	}

	this.isStopped = false;
	var jobs = this.getJobs( numJobs );
	if (!jobs || !jobs.length)
	    return;


	this.log( "jobs queued (%i): ", this.jobQueue.length, this.jobQueue );
	this.log( "jobs pending: ", Object.keys( this.jobsPending ) );
	this.log( "jobs being started: ", jobs );

	var jobsStarting = [];
	var job, jobId, jobRunner, delay;

	for (var i = 0; i < jobs.length; i++)
	{
		jobId = jobs[ i ];
		job = this.jobs[ jobId ];
		if (!job) continue;

		job.runner = this.createJobRunner( jobId, job );
		jobsStarting.push( job );
	}

	this.numJobsRunning += jobsStarting.length;
	for (var i in jobsStarting)
	{
		job = jobsStarting[ i ];
		delay = job.options.delay || this.options.delay || 0;
		this.log( "starting job %s, delay = %s", jobId, delay );
		this.jobsPending[ jobId ] = setTimeout( job.runner, delay );
	}
};


ChainLoader.prototype.log = function( str )
{
	if (!this.options.debug) return;

	var now = Date.now();
	if (!this._last) this._last = now;

	var elapsed = now - this._last;
	var templ = elapsed + ": " + str;

	var args = Array.prototype.splice.call( arguments, 0 );
	args[0] = templ;

	console.log.apply( console, args );
};


ChainLoader.prototype.createJobRunner = function( jobId, job )
{
	return function()
	{
		delete this.jobsPending[ jobId ];
		delete this.jobs[ jobId ];
		delete job.runner;

		job.jobFunc.call();

		delete job.jobFunc;
	}
	.bind( this );
};


ChainLoader.prototype.loadNext = function()
{
	this.numJobsRunning--;
	if (this.numJobsRunning < 0)
	{
		console.warn( this.numJobsRunning );
		this.numJobsRunning = 0;
	}

	if (this.isStopped)
		return;

	if (this.jobQueue.length > 0)
		this.load();

	if (this.isFinished())
	{
		this._last = 0;
		jQuery( this ).triggerHandler( 'finish.loading' );
	}
};


ChainLoader.prototype.cancelPending = function()
{
	for (var jobId in this.jobsPending)
	{
		var timerId = this.jobsPending[ jobId ];
		if (timerId)
		{
			clearTimeout( timerId );
			delete this.jobsPending[ jobId ];
		}
	}
};


ChainLoader.prototype.stop = function( /*boolean*/ shouldCancelPending )
{
	this.isStopped = true;
	if (shouldCancelPending)
	{
		this.cancelPending();
	}
};


ChainLoader.prototype.isFinished = function()
{
	return (this.jobQueue.length == 0 && this.numJobsRunning == 0);
};



/*~~~~~~~~~~~~~~~ class ChainLoader.Image extends ChainLoader ~~~~~~~~~~~~~~~~~~~*/

/**
*   Subclass of {ChainLoader} for loading {Image}s. Typical usage:
*
*       var loader = new ChainLoader.Image( { numConcurrentJobs: 3 } );
*       var image = new Image();
*       loader.schedule( "arbitrary jobId", imageUrl, image );
*       // etc...
*       loader.load();
*/
ChainLoader.Image = function() { ChainLoader.apply( this, arguments ); };

ChainLoader.Image.prototype = new ChainLoader;
ChainLoader.Image.prototype.constructor = ChainLoader;


/** Overridden version of ChainLoader.schedule(). */
ChainLoader.Image.prototype.schedule =
function( jobId, /*string*/ url, /*Image*/ image, /*Map?*/ options )
{
	if (!image || !(image instanceof HTMLImageElement))
	{
		throw new Error( "image argument not a HTMLImageElement" );
	}

	var im = jQuery( image );

	var chainloaderCallback = function()
	{
		this.log( "finished job '%s'", jobId );

		im.unbind( 'load', chainloaderCallback );
		im.unbind( 'error', chainloaderCallback );
		im.unbind( 'abort', chainloaderCallback );

		this.loadNext();
	}
	.bind( this );

	im.on({
		load: chainloaderCallback,
		error: chainloaderCallback,
		abort: chainloaderCallback,
	});

	ChainLoader.prototype.schedule.call( this, jobId, function() {
		image.src = url;
	}, options );
};


// runnable examples
/*
var a = new ChainLoader( { numConcurrentJobs: 2 } );
for (var i = 0; i < 10; i++ )
{
	a.schedule( i, function() { console.log( "job done" ); a.loadNext(); } );
}

a.load();
*/
// a.schedule( 2, function() { this.log( 2 ); a.loadNext(); } );
// a.schedule( 3, function() { this.log( 3 ); a.loadNext(); } );

/*

var b = new ChainLoader( { numConcurrentJobs: 3, delay: 10 } );
for (var i = 0; i < 10; i++ )
{
	var x = i;
	b.schedule( i, function() {
		// console.log( "job done" );
		var im = new Image();
		im.onload = function() { console.log( "loaded ", this.src ); im.onload = null; b.loadNext(); };
		im.src = "http://10.40.1.102:8083/sv/static/tiles/spaces/minspec/1000/5/" +
				x + "/" + x + ".jpg"
	});
}

b.load();
*/

/*

var c;
var imgList;

c = new ChainLoader.Image( { numConcurrentJobs: 3, delay: 0, debug: 1 } );
imgList = [];
c._last = 0;

for (var i = 0; i < 20; i++ )
{
	var id = "5:" + i + ":" + i;
	var url = "http://10.40.1.102:8083/sv/static/tiles/spaces/minspec/5/" +
				i + "/" + i + ".jpg";

	var im = new Image();
	jQuery( im ).one( 'load', function() { imgList.push( this ); } );

	c.schedule( id, url, im );
}

c.load();

*/
