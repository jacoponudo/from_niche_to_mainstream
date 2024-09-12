# Import
data <- read_csv("facebook_size_vs_iac.csv")
data=data[,2:3]

hist((data$IAC))
hist((data$size))


library(dplyr)
data <- data %>% filter(!is.na(IAC) & !is.na(size) & IAC > 0 & size > 0)

model <- lm((IAC) ~ (size), data=data)
summary(model)
