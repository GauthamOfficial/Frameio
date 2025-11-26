// Stub module to replace canvas package in client-side builds
// canvas is a Node.js-only package that fabric.js optionally uses
// This stub prevents webpack from trying to bundle the native .node file

module.exports = {};

