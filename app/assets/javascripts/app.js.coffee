#= require backbone-rails
#= require evrobone/app-class
#= require evrobone/app-mixins/views-management
#= require evrobone/app-mixins/custom-element-binding
#= require evrobone/app-mixins/window-navigation
#= require evrobone/app-mixins/window-refresh
#= require_self

class AppClass extends Evrobone.AppClass

  @include Evrobone.AppMixins.ViewsManagement, 'viewsManagement'
  @include Evrobone.AppMixins.CustomElementBinding, 'customElementBinding'
  @include Evrobone.AppMixins.WindowNavigation
  @include Evrobone.AppMixins.WindowRefresh

  warnOnMultibind: false
  groupBindingLog: false

window.App = new AppClass('evrone')
