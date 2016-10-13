class CreateImages < ActiveRecord::Migration[5.0]
  def change
    create_table :images do |t|
      t.string :foto
      t.jsonb :colorizer_result
      t.timestamps
    end
  end
end
