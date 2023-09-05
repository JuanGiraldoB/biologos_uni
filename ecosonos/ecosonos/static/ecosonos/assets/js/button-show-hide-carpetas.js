jQuery(function($) {
  $('#swapFire').on('click', function() {
    var $el = $(this),
      textNode = this.lastChild;
    $el.find('span').toggleClass('glyphicon-folder-close glyphicon-folder-open');
    textNode.nodeValue = ($el.hasClass('showFire') ? 'Deseleccionar' : 'Seleccionar') + ' Carpetas '
    $el.toggleClass('showFire');
  });
});