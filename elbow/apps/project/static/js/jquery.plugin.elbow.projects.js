'use strict';
/*
jQuery.getScript( "//cdnjs.cloudflare.com/ajax/libs/handlebars.js/4.0.6/handlebars.min.js", function( data, textStatus, jqxhr ) {
    jQuery.getScript( "//app.today-capital.eu/static/js/jquery.plugin.elbow.projects.js", function( data, textStatus, jqxhr ) {
        jQuery('body > div.main_wrapper > div.container.page > div > div > div.span4 > div.project-info-wrapper > div.project-info').projects({
            endpoint: 'https://app.today-capital.eu/de/api/v1/projects/todayhaus/',
            source: '<table id="tablepress-7" class="tablepress tablepress-id-7">' +
                '<tbody>' +
                '<tr class="row-1">' +
                '    <td class="column-1">{{ revenue.amount }} €</td>' +
                '</tr>' +
                '<tr class="row-2">' +
                '    <td class="column-1">von {{ amount.amount }} € investiert</td>' +
                '</tr>' +
                '<tr class="row-3">' +
                '    <td class="column-1">9 Wochen verbleiben</td>' +
                '</tr>' +
                '<!--<tr class="row-4">' +
                '    <td class="column-1"><img src="//today-capital.de/wp-content/uploads/2016/07/tc-progress-bar-00.png" alt="tc-progress-bar-00" width="256" height="16" class="alignnone size-full wp-image-443"></td>' +
                '</tr>-->' +
                '<tr class="row-5">' +
                '    <td class="column-1"><div style="background-color:#94c11f;padding:16px;border-radius:8px;text-align:center;"><a href="{{ urls.invest_now }}?TB_iframe=true&amp;width=1024&amp;height=768" class="thickbox" style="color:#ffffff;font-size:150%;">Jetzt investieren</a></div></td>' +
                '</tr>' +
                '</tbody>' +
                '</table>'
        });
    });
});
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
            this.project();
        },
        _listen: function () {
        },
        project: function () {
            var self = this;
            $.ajax({
                type: 'GET',
                url: self.options.endpoint,
                beforeSend: function () {
                },
                success: function ( data ) {
                    self._log(data);
                    self._log('fdaffds');
                    var combined_html = '';
                    var html = self.template(data)
                    self.element.html(html);
                    
                },
                error: function ( data ) {
                    self._log(data);
                },
                complete: function (data) {
                    self._log(data);
                }
            });
        }

    });
});