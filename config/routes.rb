Rails.application.routes.draw do

  post '/images/upload', to: 'images#upload'
  get  '/images/upload', to: 'images#upload'

  resources :images
end
