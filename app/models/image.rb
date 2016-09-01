class Image < ApplicationRecord
  mount_uploader :foto, FotoUploader
end
