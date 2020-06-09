var glide = new Glide('.glide',{
    type: 'slider',
    focusAt: 'center',
    perView: 3,
    autoplay: 2000,
    gap: 30,
    breakpoints: {
        767:{
            perView: 1,
        }
    }
})

glide.mount()