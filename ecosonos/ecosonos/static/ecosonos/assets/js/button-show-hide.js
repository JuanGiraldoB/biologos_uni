jQuery(function($) {
  $('#swapFire').on('click', function() {
    var $el = $(this),
      textNode = this.lastChild;
    $el.find('span').toggleClass('glyphicon-eye-close glyphicon-eye-open');
    textNode.nodeValue = ($el.hasClass('showFire') ? 'Mostrar' : 'Ocultar') + ' Gráfica '
    $el.toggleClass('showFire');
  });
});