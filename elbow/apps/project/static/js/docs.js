(function ($) {
  'use strict';

  $( document ).ready(function() {

    $('.require-logged-in').on('click', function (e) {
      $(this).addClass('alert alert-warning')
    });

  });

})(jQuery);
