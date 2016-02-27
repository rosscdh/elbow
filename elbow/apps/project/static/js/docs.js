(function ($) {
  'use strict';

  $( document ).ready(function() {

    $('.require-logged-in').on('click', function (e) {
      var notice = $($(this).parents().find('.notice:first'));
      notice.removeClass('hide');
      notice.fadeIn().delay(5000).fadeOut();
    });

 });

})(jQuery);
