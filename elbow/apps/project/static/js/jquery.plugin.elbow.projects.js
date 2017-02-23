'use strict';
/*
*/
jQuery(function($) {
    // the widget definition, where "custom" is the namespace,
    // "colorize" the widget name
    $.widget( "elbow.projects", {
        // default options
        options: {
            endpoint: 'http://localhost:8009/api/v1/projects/',
            source: null
        },
        _log: function (msg) {
            var self = this;
            if (self.options.debug === true) {
                console.log(msg)
            }
        },
        // the constructor
        _create: function() {
            var self = this;
            self.template = Handlebars.compile(self.options.source)
            this._listen();
            //this.projects();
        },
        _listen: function () {
        },
        projects: function () {
            var self = this;
            $.ajax({
                type: 'GET',
                url: self.options.endpoint,
                beforeSend: function () {
                },
                success: function ( data ) {
                    var combined_html = '';
                    $.each(data.results, function (i, item) {
                        console.log(i)
                        console.log(item)
                        var html = self.template(item);
                        console.log(html)
                        combined_html += html;
                    });
                    self.element.html(combined_html);
                    
                },
                error: function ( data ) {
                },
                complete: function () {
                }
            });
        },
        project: function (pk) {
            var self = this;
            $.ajax({
                type: 'GET',
                url: self.options.endpoint + pk,
                beforeSend: function () {
                },
                success: function ( data ) {
                    var combined_html = '';
                    $.each(data.results, function (i, item) {
                        console.log(i)
                        console.log(item)
                        var html = self.template(item);
                        console.log(html)
                        combined_html += html;
                    });
                    self.element.html(combined_html);
                    
                },
                error: function ( data ) {
                },
                complete: function () {
                }
            });
        }

    });
});