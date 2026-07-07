const path = require('path');

module.exports = {
    entry: './app/src/main.js',
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'app/src'), // Explicitly targets your serving directory
        library: 'eventrioChat',
        libraryTarget: 'var',
    },
    mode: 'development' // Add this to suppress the Webpack warning in your terminal
};