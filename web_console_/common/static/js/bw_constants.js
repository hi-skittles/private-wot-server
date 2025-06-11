"use strict";

console.assert( window.jQuery );

var BW = window.BW || {};


/**
 * Constants definition used across WebConsole JavaScripts 
 */
BW.Constants = BW.Constants || {};



/** 
 * HTTP response code from WebConsole server, also defined in
 * root/controllers.py
 */
BW.Constants.HTTP_RESPONSE_CODE =
{
	"Exception": 500,
	"NotImplementedError": 501,
	"AuthenticationException": 403,
	"AuthorisationException": 403,
	"ServerStateException": 455,
};


