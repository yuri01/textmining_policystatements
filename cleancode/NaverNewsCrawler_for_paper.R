install.packages("stringr")
if (!require("devtools")) install.packages("devtools")
devtools::install_github("forkonlp/N2H4")
library(N2H4)
library("stringr")
Sys.setlocale("LC_COLLATE", "ko_KR.UTF-8")
setwd("C:/Users/Ri/Dropbox/paper/R_crawling_result")
getwd()
# q<-"통화정책"
# tar <- getQueryUrl(q)

# Generate URL to collect news which including "한은" & "한국은행"
getURL=function(MPCdate){
  A<-"%C7%D1%C0%BA" #한은
  B<-"%C7%D1%B1%B9%C0%BA%C7%E0" #한국은행
  url<-paste("http://news.naver.com/main/search/search.nhn?refresh=&so=rel.dsc&stPhoto=&stPaper=&stRelease=&ie=MS949&detail=0&rcsection=&query=",A,"%2C+", B, "&sm=all.basic&pd=4&startDate=", MPCdate,"&endDate=", MPCdate, sep="")
  
  return(url)
}

# Collet news data by url
newscrawling<-function(tar){
  maxPage <- getMaxPageNum(tar)
  #
  for (i in 1:maxPage){
    tarp <- paste0(tar,"&page=",i)
    newsList<-getUrlListByQuery(tarp)
    newsData<-c()
    for (newslink in newsList$news_links){
      tryi<-0
      tem<-try(getContent(newslink), silent = TRUE)
      while(tryi<=5&&class(tem)=="try-error"){
        tem<-try(getContent(newslink), silent = TRUE)
        tryi<-tryi+1
        print(paste0("try again: ",newslink))
      }
      if(class(tem$datetime)[1]=="POSIXct"){
        newsData<-rbind(newsData,tem)
      }
    }
    dirname=paste0("./",str_sub(tar,-10,-1))
    dir.create(dirname,showWarnings=F)
    # write.csv(newsData, file=paste0("./data/news_",q,"_",i,".csv"),row.names = F, fileEncoding="UTF-8")
    write.csv(newsData, file=paste0(dirname,"/",str_sub(tar,-10,-1),"_",i,".csv"),row.names = F, fileEncoding="UTF-8")
    print(str_sub(tar,-10,-1))
  }
}


###################################################################################################

# Run code: collect news on MPC dates
MPCdates<-read.csv(file="C:/Users/Ri/Dropbox/paper/MPCdates.csv", header=FALSE, sep=",")
MPCdates[1]<-"20170413"
MPCdates<-sapply(MPCdates, as.character)

for (j in 1:length(MPCdates)){
  x=MPCdates[j]
  y=c(substring(x, first=1, last=4),substring(x, first=5, last=6),substring(x, first=7, last=8))
  mpcDate<-paste0(y, collapse="-")
  tar=getURL(mpcDate)
  maxPage <- getMaxPageNum(tar)
  
  for (i in 1:maxPage){
    tarp <- paste0(tar,"&page=",i)
    newsList<-getUrlListByQuery(tarp)
    newsData<-c()
    for (newslink in newsList$news_links){
      tryi<-0
      tem<-try(getContent(newslink), silent = TRUE)
      # while(tryi<=5&&class(tem)=="try-error"){
      #   tem<-try(getContent(newslink), silent = TRUE)
      #   tryi<-tryi+1
      #   print(paste0("try again: ",newslink))
      # }
      if(class(tem)=="try-error"){
        break
      }
      
      if(class(tem$datetime)[1]=="POSIXct"){
        newsData<-rbind(newsData,tem)
      }
    }
    dirname=paste0("./",str_sub(tar,-10,-1))
    dir.create(dirname,showWarnings=F)
    # write.csv(newsData, file=paste0("./data/news_",q,"_",i,".csv"),row.names = F, fileEncoding="UTF-8")
    write.csv(newsData, file=paste0(dirname,"/",str_sub(tar,-10,-1),"_",i,".csv"),row.names = F, fileEncoding="UTF-8")
    print(str_sub(tar,-10,-1))
    print(maxPage)
  }
}





