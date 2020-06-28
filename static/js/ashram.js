// INITIALIZE PHOTOSWIPE

var pswpInit = function(startsAtIndex){

    if (!startsAtIndex) startsAtIndex = 0;

    var pswpElement = document.querySelectorAll('.pswp')[0];

    // find is images are loaded from the server.
    if (window.djangoAlbumImages && window.djangoAlbumImages.length > 0) {
        // define options (if needed)
        var options = {
            // optionName: 'option value'
            // for example:
            index: startsAtIndex
        };

        // Initializes and opens PhotoSwipe
        var gallery = new PhotoSwipe( pswpElement, PhotoSwipeUI_Default, window.djangoAlbumImages, options);
        gallery.init();
    }

}
