
library(tools)

pkg_path <- commandArgs(trailingOnly = TRUE)[1]
vignettes_path <- paste(pkg_path, "/vignettes/", sep="")

rmd_files <- list.files(path = vignettes_path, pattern = "\\.Rmd$", full.names = FALSE, recursive = TRUE)
setwd(vignettes_path)
for (f in rmd_files){
    name <- paste(file_path_sans_ext(f), ".qmd", sep="")
    # name <- gsub("_", "-", name)
    print(name)
    rmarkdown::render(input = f, output_format = "github_document", output_file = name)
}
