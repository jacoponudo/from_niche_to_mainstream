# Load the .rData file
load('/media/jacoponudo/Elements/facebook_news/OriginalData/all_comments.rData')

# Campionamento di 1000 valori unici di post_id
sampled_post_ids <- sample(unique(all_comments$post_id), size = 100000, replace = FALSE)



# Filtrare il sottoinsieme con i post_id campionati
comments_sampled_subset <- all_comments[all_comments$post_id %in% sampled_post_ids, ]


library(arrow)

# Supponiamo che il tuo dataframe si chiami 'df'
write_parquet(comments_sampled_subset, "~/Documents/Size_effects/DATA/facebook/facebook_raw_data.parquet")
