plot_polar_indices <- function(xdata, indices2plot,
                                       path_plots_html=NA,
                                       path_plots_pdf=NA, ...){
  df_api <- xdata%>%
    mutate(h_FI = as.integer(format(
      as.POSIXct(time_FI), format = "%H")))
  
  if('rain_FI' %in% colnames(xdata)){
    df_api_nrain <- xdata %>%
      filter(rain_FI=='NO')%>%
      mutate(h_FI = as.integer(format(
        as.POSIXct(time_FI), format = "%H")))
  }
  else{
    df_api_nrain <- NA
  }
  
  for(indice in indices2plot){
    print(indice)
    df2plot <- df_api %>%
      select(field_number_PR, date_FI, h_FI, indice_=all_of(indice))
    
    df2plot <- df2plot%>%
      group_by(field_number_PR, date_FI, h_FI) %>%
      summarize(value = mean(indice_, na.rm=TRUE))
    
    base_plot <- ggplot(df2plot,aes(x=h_FI,y=date_FI,fill=value))+
      geom_tile()+
      scale_x_continuous(breaks=seq(0,23,2))+
      theme_classic() +
      scale_fill_gradientn( colours = c("#0100FF", "#00FF25",
                                        "#F4FF00", "#FF0000")) +
      theme_minimal()+
      labs(x='', y='', title = indice)+
      facet_wrap(~ field_number_PR) + coord_polar()
    
    name2save <- paste("Polar_", indice, sep='')
    
    if(!is.na(name2save)){
      if(!is.na(path_plots_pdf)){
        path_pdf_file <- file.path(path_plots_pdf, paste(name2save, '.pdf'))
        ggsave(path_pdf_file, ...)
      }
    }
    
    base_plot <- ggplot(df2plot,aes(x=h_FI,y=date_FI,fill=value))+
      geom_tile()+
      scale_x_continuous(breaks=seq(0,23,2))+
      theme_classic() +
      scale_fill_gradientn( colours = c("#0100FF", "#00FF25",
                                        "#F4FF00", "#FF0000")) +
      theme_minimal()+
      labs(x='', y='', title = indice)+
      facet_wrap(~ field_number_PR)
    
    name2save <- paste("Cartesian_", indice, sep='')
    
    if(!is.na(name2save)){
      if(!is.na(path_plots_pdf)){
        path_pdf_file <- file.path(path_plots_pdf, paste(name2save, '.pdf'))
        ggsave(path_pdf_file, ...)
      }
    }
    
    if(is.data.frame(df_api_nrain)){
      df2plot <- df_api_nrain %>%
        select(field_number_PR, date_FI, h_FI, indice_=all_of(indice))
      
      df2plot <- df2plot%>%
        group_by(field_number_PR, date_FI, h_FI) %>%
        summarize(value = mean(indice_, na.rm=TRUE))
      
      base_plot <- ggplot(df2plot,aes(x=h_FI,y=date_FI,fill=value))+
        geom_tile()+
        scale_x_continuous(breaks=seq(0,23,2))+
        theme_classic() +
        scale_fill_gradientn( colours = c("#0100FF", "#00FF25",
                                          "#F4FF00", "#FF0000")) +
        theme_minimal()+
        labs(x='', y='', title = indice)+
        facet_wrap(~ field_number_PR) + coord_polar()
      
      name2save <- paste("Polar_NoLluvia_", indice, sep='')
      
      if(!is.na(name2save)){
        if(!is.na(path_plots_pdf)){
          path_pdf_file <- file.path(path_plots_pdf, paste(name2save, '.pdf'))
          ggsave(path_pdf_file, ...)
        }
      }
      
      base_plot <- ggplot(df2plot,aes(x=h_FI,y=date_FI,fill=value))+
        geom_tile()+
        scale_x_continuous(breaks=seq(0,23,2))+
        theme_classic() +
        scale_fill_gradientn( colours = c("#0100FF", "#00FF25",
                                          "#F4FF00", "#FF0000")) +
        theme_minimal()+
        labs(x='', y='', title = indice)+
        facet_wrap(~ field_number_PR)
      
      name2save <- paste("Cartesian_NoLluvia_", indice, sep='')
      
      if(!is.na(name2save)){
        if(!is.na(path_plots_pdf)){
          path_pdf_file <- file.path(path_plots_pdf, paste(name2save, '.pdf'))
          ggsave(path_pdf_file, ...)
        }
      }
    }
  }
}