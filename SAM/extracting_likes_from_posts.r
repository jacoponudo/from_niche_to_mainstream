posts=read.csv('~/Documents/repository/size-effect/SAM/sample/sample_posts.csv',colClasses = "character")
posts=unique(posts$post_id)

folder_path <- "/media/gabett/Elements/facebook_news/OriginalData/LikesCSV/"
file_list <- list.files(path = folder_path, pattern = "*.csv", full.names = TRUE)
all_filtered_data <- map_df(file_list, filter_data_post)
write.csv(all_filtered_data,'~/Documents/repository/size-effect/SAM/sample/sample_likes.csv')
