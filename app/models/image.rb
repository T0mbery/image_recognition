class Image < ApplicationRecord
  mount_uploader :foto, FotoUploader

  validates :foto, presence: true
end
