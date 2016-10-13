class ImagesController < ApplicationController
  
  def index
    @images = Image.all
  end
  
  def show
    @image = Image.find(params[:id])
    respond_to do |format|
      format.html {  }
    end
  end
  
  def create
    begin
      @image = Image.create(image_params)
    rescue FotoUploader::FaceIsNotDetected
      flash[:notice] = 'Не удалось распознать лицо'
    rescue FotoUploader::DetectionAlgorithm
      flash[:notice] = 'Не удалось распознать контур.'
    end
    redirect_to action: 'index'
  end
  
  def destroy
    @image = Image.find(params[:id])
    @image.destroy
    redirect_to action: 'index'
  end
  
  private

  def image_params
    params.permit(:foto)
  end

end
