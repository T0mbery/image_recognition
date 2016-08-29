class ImagesController < ApplicationController
  
  def index
  end

  def upload
    if image = params[:image]
      image_path = image.original_filename
      
      File.open(Rails.root.join('app', 'assets', 'images', image_path), 'wb') do |file|
        file.write(image.read)
      end

      detect_contour(image_path)
    else
      redirect_to action: 'index'
    end
  end
  
  private
  
  def detect_contour(image_path)
    require "opencv"
    
    field_path = Rails.root.join('app', 'assets', 'images')

    cvmat = OpenCV::CvMat.load("#{field_path + image_path}")
    cvmat = cvmat.BGR2GRAY
    canny = cvmat.canny(370, 1000)

    contour = canny.find_contours(:mode => OpenCV::CV_RETR_LIST, :method => OpenCV::CV_CHAIN_APPROX_SIMPLE)

    while contour
      # No "holes" please (aka. internal contours)
      unless contour.hole?

        puts '-' * 80
        puts "BOUNDING RECT FOUND"
        puts '-' * 80

        # You can detect the "bounding rectangle" which is always oriented horizontally and vertically
        box = contour.bounding_rect
        puts "found external contour with bounding rectangle from #{box.top_left.x},#{box.top_left.y} to #{box.bottom_right.x},#{box.bottom_right.y}"

        # The contour area can be computed:
        puts "that contour encloses an area of #{contour.contour_area} square pixels"

        # .. as can be the length of the contour
        puts "that contour is #{contour.arc_length} pixels long "

        # Draw that bounding rectangle
        cvmat.rectangle! box.top_left, box.bottom_right, :color => OpenCV::CvColor::Red

        # You can also detect the "minimal rectangle" which has an angle, width, height and center coordinates
        # and is not neccessarily horizonally or vertically aligned.
        # The corner of the rectangle with the lowest y and x position is the anchor (see image here: http://bit.ly/lT1XvB)
        # The zero angle position is always straight up. 
        # Positive angle values are clockwise and negative values counter clockwise (so -60 means 60 degree counter clockwise)
        box = contour.min_area_rect2
        puts "found minimal rectangle with its center at (#{box.center.x.round},#{box.center.y.round}), width of #{box.size.width.round}px, height of #{box.size.height.round} and an angle of #{box.angle.round} degree"
      end
      contour = contour.h_next
    end

    cvmat.save_image("#{field_path}/img-#{image_path}")
    @detected_img_path = 'img-' + image_path
    
  end
end
