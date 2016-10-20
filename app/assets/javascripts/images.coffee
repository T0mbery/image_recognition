class App.Views.Images extends App.View
  el: '.cards'

  events:
    'mouseover   .js-card': 'changeCard'
    'mouseout    .js-card': 'changeCardBack'


  changeCard: (event) ->
    card = $(event.currentTarget)
    recognition_img_src  = card.attr('src')
    recognition_img_src_split = recognition_img_src.split('/')
    recognition_img_name = recognition_img_src_split[5].split('_')
    recognition_img_name[0] = 'contour'
    
    thumb_img_name_join = recognition_img_name.join('_')
    recognition_img_src_split[5] = thumb_img_name_join
    
    thumb_img_src = recognition_img_src_split.join('/')

    card.attr('src', thumb_img_src)

  changeCardBack: (event) ->
    card = $(event.currentTarget)
    thumb_img_src  = card.attr('src')
    thumb_img_src_split = thumb_img_src.split('/')
    thumb_img_name = thumb_img_src_split[5].split('_')
    thumb_img_name[0] = 'recognition'

    recognition_img_name_join = thumb_img_name.join('_')
    thumb_img_src_split[5] = recognition_img_name_join

    recognition_img_src = thumb_img_src_split.join('/')

    card.attr('src', recognition_img_src)

