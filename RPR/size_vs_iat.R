# Import
library(readr)
data <- read_csv("facebook_size_vs_iat.csv")
data=data[,2:3]

hist(log(data$IAT))
hist((data$size))


library(dplyr)
data <- data %>% filter(!is.na(IAT) & !is.na(size) & IAT > 0 & size > 0)

model <- lm(log(IAT) ~ log(size), data=data)
summary(model)



coef(model)
(2.3925225+log(50)*(-0.1334878)  )
(2.3925225+log(200)*(-0.1334878 ) )
