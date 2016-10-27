class AddDataColumnToImage < ActiveRecord::Migration[5.0]
  def change
    add_column :images, :data, :jsonb
  end
end
