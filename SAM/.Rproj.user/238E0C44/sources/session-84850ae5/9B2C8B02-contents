source("funcions.r")
posts=read.csv('~/Documents/Size_effects/SAM/sample/sample_posts.csv',colClasses = "character")
posts=unique(posts$post_id)

folder_path <- "/media/jacoponudo/Elements/facebook_news/OriginalData/CommentsCSV/"
file_list <- list.files(path = folder_path, pattern = "*.csv", full.names = TRUE)
all_filtered_data <- map_df(file_list, filter_data_post)
write.csv(all_filtered_data,'~/Documents/Size_effects/SAM/sample/sample_comments.csv')


