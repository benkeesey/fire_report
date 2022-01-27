
import numpy as np
import report_markdown as md

import holoviews as hv, panel as pn
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

class Visualization(object):

    def __init__(self, color_scheme, time_window, name, **argd):
        """
        Constructs all the necessary attributes for the fire report from the passed dict.
        """
        self.color_scheme = color_scheme
        self.name = name
        self.time_window = time_window
        # Call color_schemes function to save color values as instance variables.
        self.color_schemes()

    def color_schemes(self): 
        """ 
        Creates specifc color variables from the color_scheme tuple dict of colors and saves the hex strings as instance variables.

        ### Color Schemes
        # Follows the following order:
        # 0-3 are the main colors
        # 4 is accent
        # 5 is an alternate color for accent
        # 6 is the background color
        # 7 is the font color 
        """ 
        color_schemes_available = {
                                'office_pastel':('#b76e79', '#87907d', '#d2a9aa', '#b6c9b3', '#e1d1d1', '#d2a9aa', '#ffffff', '#535253'),
                                'mountain_range':('#a84729', '#456c3d', '#62341e', '#848a56', '#b3995b', '#d29057', '#b0bb9b', '#0F0F0F'),
                                'xerox':('#242424', '#494949', '#404048', '#282828', '#e2e6e6', '#b6b6b6', '#ffffff', '#000000'),
                                'stickies':('#f6114a', '#1fa2ff', '#3333ff', '#661fff', '#ddbea9', '#eb8258', '#ffffff', '#2d3047'),
                                'miami_sunrise':('#fb8500', '#5390d9', '#f8961e', '#f9c74f', '#f79d84', '#C8D7FF', '#FFF5D6', '#023047')
                                }
        if self.color_scheme in color_schemes_available:
            color_tuple = color_schemes_available[self.color_scheme]
            # return color_schemes_available[self.color_scheme]
        else:
            import warnings
            warnings.warn("Warning! No valid color scheme picked, default selected.\nPlease pick from the following choices:\noffice_pastel\nmountain_range\nxerox\nstickies\nmiami_sunrise")
            color_tuple = color_schemes_available[self.color_scheme]
            # return color_schemes_available['stickies']
        
        self.color_1 = color_tuple[0]
        self.color_2 = color_tuple[1]
        self.color_3 = color_tuple[2]
        self.color_4 = color_tuple[3]
        self.color_accent = color_tuple[4]
        self.color_alt = color_tuple[5]
        self.color_background = color_tuple[6]
        self.color_font = color_tuple[7]


    def spending_fire_plot(self, df, file_name):
        """ 
        Creates a plot using matplotlib to track the Monte Carlo growth of models returned by the Monte_Carlo_Plot_Spending function. 
        Saves a png of the plot in the Assets folder in the directory.
        
        # Parameters:
            df : pandas DataFrame object, default None
                pandas DataFrame output from Monte_Carlo_Plot_Spending function for various Monte Carlo simulated returns.

            file_name : str, default None
                If not provided '{Users Name}'s Monte Carlo Plot' is used.
                
        # Returns:
            None
        """  
        plt.figure(figsize=(25, 10), dpi=80)
        plt.ylabel('Balance Available')
        plt.xlabel('Years')
        plt.grid(visible=True, color=self.color_accent)

        ax = plt.gca()

        # X-Axis Formatting
        ax.set_facecolor(self.color_background)
        ax.xaxis.label.set_color(self.color_font)
        ax.tick_params(axis='x', colors=self.color_font)
        ax.set_xticks(np.arange(1, df.shape[1]+1, step=1), minor=False)
        # Y-Axis Formatting
        ax.yaxis.label.set_color(self.color_font)
        ax.tick_params(axis='y', colors=self.color_font)


        ax.axis(xmin=1,xmax=df.shape[1]+1, ymin=0, ymax=df.max().max())
        ax.ticklabel_format(axis='both', style='sci', scilimits=(1,10), useOffset=None, useLocale=None, useMathText=None)


        ax.yaxis.set_major_formatter(StrMethodFormatter('${x:,.0f}')) # No decimal places with dollar sign
        ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}')) # No decimal places with dollar sign

        plt.plot(df.T, color=self.color_accent)

        # Get the Average across all models
        mean_model = df.mean(axis=0)
        plt.plot(mean_model, linestyle='dashed', linewidth=5, color=self.color_1, label='Average Value')
        ax.legend(labelcolor=[self.color_1], loc='upper left', edgecolor=self.color_font, facecolor=self.color_background)

        # Annotate the Average line
        num = mean_model.iloc[-1].round(0)
        currency_string = "Average\nEnding\nBalance:\n${:,.0f}".format(num)
        plt.annotate(currency_string, (df.shape[1]+.1,num), color=self.color_1, verticalalignment='center')

        # plt.show()
        if file_name is None:
            file_name=f"{self.name}'s' Monte Carlo Plot"
        plt.savefig(f'{file_name}.png', dpi=80, facecolor=self.color_background, bbox_inches='tight', pad_inches=0)


    def Monte_Carlo_Plot_Growth_Comparison(self, account1, account1_name, account2, account2_name, cash_account):
        """ 
        Creates a plot using matplotlib to compare multiple Monte Carlo growths using similar parameters. 
        Used to show a comparison of growth between different tax advantage accounts using otherwise similar parameters.
        
        # Parameters:
            account1 : pandas DataFrame object, default None
                pandas DataFrame output from Monte_Carlo_Growth_Models function for the first account to compare.

            account1_name : str, default None
                Name to display for for the lables to identify what kind of account it is.
                
            account2 : pandas DataFrame object, default None
                pandas DataFrame output from Monte_Carlo_Growth_Models function for the second account to compare.

            account2_name : str, default None
                Name to display for for the lables to identify what kind of account it is.

            cash_account : pandas DataFrame object, default None
                pandas DataFrame output from cash_balance function to model show the cash deposits over time with no investment.

        # Returns:
            None
        """  
        # Start of Matplotlib Figure
        plt.figure(figsize=(25, 10), dpi=80)
        plt.ylabel('Balance Available')
        plt.xlabel('Years')
        plt.grid(visible=True, color=self.color_accent)

        ax = plt.gca()

        # X-Axis Formatting
        ax.set_facecolor(self.color_background)
        ax.xaxis.label.set_color(self.color_font)
        ax.tick_params(axis='x', colors=self.color_font)
        
        max_xaxis_val = max([account1.shape[0], account2.shape[0]])
        max_yaxis_val = max(account1.max().max(), account2.max().max())
        
        ax.set_xticks(np.arange(1, (max_xaxis_val)+1, step=1), minor=False)
        # Y-Axis Formatting
        ax.yaxis.label.set_color(self.color_font)
        ax.tick_params(axis='y', colors=self.color_font)

        
        ax.axis(xmin=1,xmax=max_xaxis_val+1, ymin=0, ymax=max_yaxis_val)
        ax.ticklabel_format(axis='both', style='sci', scilimits=(1,10), useOffset=None, useLocale=None, useMathText=None)


        ax.yaxis.set_major_formatter(StrMethodFormatter('${x:,.0f}')) # No decimal places with dollar sign
        ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}')) # No decimal places with dollar sign

        plt.plot(account1, color=self.color_accent)
        plt.plot(account2, color=self.color_alt)
        
        # TODO: Include the other accounts in this comparison
        # plt.plot(Roth_models_df, color=color_alt)
        # plt.plot(Trad_401k_models_df, color=color_alt)

        # Get the HSA average across all models
        account1_Mean_Model = account1.mean(axis=1)
        plt.plot(account1_Mean_Model, linestyle='dashed', linewidth=5, color=self.color_1, label=f'{account1_name} Model')

        # Annotate the HSA Average line
        num = account1_Mean_Model.iloc[-1].round(0)
        currency_string = "Average {}\nEnding\nBalance:\n${:,.0f}".format(account1_name,num)
        plt.annotate(currency_string, (self.time_window+.1,num), color=self.color_1, verticalalignment='center')

        # Get the Brokerage average across all models
        account2_Mean_Model = account2.mean(axis=1)
        plt.plot(account2_Mean_Model, linestyle='dashed', linewidth=5, color=self.color_2, label=f'{account2_name} Model')

        # Annotate the Brokerage Average line
        num = account2_Mean_Model.iloc[-1].round(0)
        currency_string = "Average {}\nEnding\nBalance:\n${:,.0f}".format(account2_name, num)
        plt.annotate(currency_string, (self.time_window+.1,num), color=self.color_2, verticalalignment='center')


        # Cash investment, showing just yearly savings
        plt.plot(cash_account, linestyle='dotted', linewidth=5, color=self.color_3, label='Cash Savings')
        ax.legend(labelcolor=[self.color_1, self.color_2, self.color_3], loc='upper left', edgecolor=self.color_font, facecolor=self.color_background)

        # Annotate the Cash Ending Balance
        num = cash_account[0].iloc[-1]
        currency_string = "Cash\nEnding\nBalance:\n${:,.0f}".format(num)
        plt.annotate(currency_string, (self.time_window+.5,num), color=self.color_3, verticalalignment='center')
        # Save Matplotlib figure as png file in Assets folder
        plt.savefig('Assets/Monte_Carlo_Plot_Growth_Comparison.png', dpi=80, facecolor=self.color_background, bbox_inches='tight', pad_inches=0)

    
    def Monte_Carlo_Plot_Spending_Statistics(self, df):
        """ Calculated the percent of models that never fall below the spending total in their modeled account balance.
        
        # Parameters:
            df : pandas DataFrame object, default None
                pandas DataFrame output from the Monte_Carlo_Plot_Spending function. Contains the modeled returns across a given time period.
                
        # Returns:
            success_percentage : Float, default None
                A float for the percentage of sucessful models that never had their account balance below the total spending series. 
            final_first_quartile : Float, default None
                A float for the 25% quantile of the last year of all the models 
            final_median : Float, default None
                A float for the median (50% quantile) of the last year of all the models 
            final_third_quartile : Float, default None
                A float for the 75% quantile of the last year of all the models 
        
        """  
        
        # First Calculate what percent of models never had a value balance  of 0
        total_models = len(df)
        # Check if any value in a row (model year) was ever 0. Then counts the number of True (never 0) and False (at least one 0).
        sucessful_models = df.all(axis=1).sum()

        # Calculate the percent of sucessful models rounded to the nearest int
        success_percentage = round(sucessful_models/total_models*100)
        
        
        # Calculate the 25%, 75% quartile and median (50% quartile) of all models for all years.
        first_quartile, median, third_quartile = np.quantile(df, [.25, .5, .75], axis=0)
        # Calculate the rounded specifc quantiles for just the ending year of the models.
        final_first_quartile = round(first_quartile[-1])
        final_median = round(median[-1])
        final_third_quartile = round(third_quartile[-1])
        
        
        self.success_percentage = success_percentage
        self.final_first_quartile = final_first_quartile
        self.final_median = final_median
        self.final_third_quartile = final_third_quartile
        
        return success_percentage, final_first_quartile, final_median, final_third_quartile


    def Dashboard(self, liquid_df, net_df, save_filename=None):
        """
        Returns a simple static dashboard as an Panel object. One column with multiple rows for relevant headers, Text, and Visuals
        Visual is also saved as a html and png file in the directories Assets folder.

        # Parameters:
        liquid_df : pandas DataFrame, default None
            DataFrame of the data used for the liquid assets spending_fire_plot. Used in this function to pass into Monte_Carlo_Plot_Spending_Statistics to show statistics over plots. 
        net_df : pandas DataFrame, default None
            DataFrame of the data used for the net assets spending_fire_plot. Used in this function to pass into Monte_Carlo_Plot_Spending_Statistics to show statistics over plots. 
        save_filename : str, default None
            parameter if you want to change filename to something other than 'HSA and Portfolio Success Analysis'.
            
        # Returns:
        dashboard : panel.Column object. 
            Returns the dashboard as a panel object if where function is run can render panel objects.
        """
        
        # Header text for the static Dashboard
        header = pn.pane.Markdown(md.header_md, style={"color": self.color_font}, width=500, 
                            sizing_mode="stretch_width", margin=(10,5,10,15))

        icon1 = pn.pane.PNG("Assets/fire.png",
                        height=60, sizing_mode="fixed", align="center")

        icon2 = pn.pane.PNG("Assets/stock-market.png", 
                        height=60, sizing_mode="fixed", align="center")

        # Put together title in a panel Row
        title = pn.Row(header, pn.Spacer(), icon1, icon2, background=self.color_background, sizing_mode='fixed', width=1250, height=70)

        # Intro paragraph giving information about the report
        intro_info = pn.pane.Markdown(md.intro_info_md, style={"color": self.color_font}, width=1250, height =300,
                                sizing_mode="scale_both", margin=(10,5,10,15))

        intro_info_row = pn.Row(intro_info, background=self.color_background, sizing_mode='fixed', width=1250, height=300)

        # Call Statistic function to get values to show in Dashboard
        # Show Statistics for Liquid Assets 
        success_percentage, final_first_quartile, final_median, final_third_quartile = self.Monte_Carlo_Plot_Spending_Statistics(liquid_df)
        # Create Markdown Text fields of the statistics to show in Dashboard
        # Change the values to show in the correct currency string format
        final_first_quartile_str = "${:,.0f}".format(self.final_first_quartile)
        final_median_str = "${:,.0f}".format(self.final_median)
        final_third_quartile_str = "${:,.0f}".format(self.final_third_quartile)
        

        liquid_stat1 = pn.pane.Markdown(f"### Successful Models:", style={"color": self.color_font}, height=70, 
                        sizing_mode="stretch_width", margin=(10,0,10,15), align='center')
        liquid_stat1_val = pn.pane.Markdown(f"# {success_percentage}%", style={"color": self.color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,5,10,0), align='center')
        
        liquid_stat2 = pn.pane.Markdown(f"#### Ending 25% Quantile Portfolio Balance:", style={"color": self.color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,0,10,15), align='center')
        liquid_stat2_val = pn.pane.Markdown(f"#{final_first_quartile_str}", style={"color": self.color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,15,10,0), align='center')

        liquid_stat3 = pn.pane.Markdown(f"#### Ending 75% Quantile Portfolio Balance:", style={"color": self.color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,0,10,15), align='center')
        liquid_stat3_val = pn.pane.Markdown(f"#{final_third_quartile_str}", style={"color": self.color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,15,10,0), align='center')

        liquid_stat_row = pn.Row(liquid_stat1, liquid_stat1_val, liquid_stat2, liquid_stat2_val, liquid_stat3, liquid_stat3_val, background=self.color_background, sizing_mode='fixed', width=1250, height=70)
        
        # Show Statistics for Net Assets 
        success_percentage, final_first_quartile, final_median, final_third_quartile = self.Monte_Carlo_Plot_Spending_Statistics(net_df)
        # Create Markdown Text fields of the statistics to show in Dashboard
        # Change the values to show in the correct currency string format
        final_first_quartile_str = "${:,.0f}".format(self.final_first_quartile)
        final_median_str = "${:,.0f}".format(self.final_median)
        final_third_quartile_str = "${:,.0f}".format(self.final_third_quartile)
        

        net_stat1 = pn.pane.Markdown(f"### Sucessful Models:", style={"color": self.color_font}, height=70, 
                        sizing_mode="stretch_width", margin=(10,0,10,15), align='center')
        net_stat1_val = pn.pane.Markdown(f"# {success_percentage}%", style={"color": self.color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,5,10,0), align='center')
        
        net_stat2 = pn.pane.Markdown(f"#### Ending 25% Quantile Portfolio Balance:", style={"color": self.color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,0,10,15), align='center')
        net_stat2_val = pn.pane.Markdown(f"#{final_first_quartile_str}", style={"color": self.color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,15,10,0), align='center')

        net_stat3 = pn.pane.Markdown(f"#### Ending 75% Quantile Portfolio Balance:", style={"color": self.color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,0,10,15), align='center')
        net_stat3_val = pn.pane.Markdown(f"#{final_third_quartile_str}", style={"color": self.color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,15,10,0), align='center')

        net_stat_row = pn.Row(net_stat1, net_stat1_val, net_stat2, net_stat2_val, net_stat3, net_stat3_val, background=self.color_background, sizing_mode='fixed', width=1250, height=70)



        # Growth Plot Header Creation
        growth_plot_title = pn.pane.Markdown(md.growth_plot_title_md, style={"color": self.color_font}, 
                        sizing_mode="fixed", margin=(10,5,5,15), width=1250, height=50)
        growth_plot_account_info = pn.pane.Markdown(md.growth_plot_account_info_md, 
        style={"color": self.color_font}, width=1250, sizing_mode="scale_both", margin=(10,5,10,15))
        
        growth_plot_header = pn.Column(growth_plot_title, growth_plot_account_info, background=self.color_background, sizing_mode='fixed', width=1250, height=300)
        
        growth_comparison_plot = pn.pane.PNG("Assets/Monte_Carlo_Plot_Growth_Comparison.png", sizing_mode="scale_both", align="center")
        growth_comparison_plot_row = pn.Row(growth_comparison_plot, background=self.color_background, width=1250)

        # FIRE Spending Plot Header Creation
        spending_plot_title = pn.pane.Markdown(md.spending_plot_title_md, style={"color": self.color_font}, width=500, height=50, 
                        sizing_mode="stretch_width", margin=(10,5,10,15))
        spending_plot_info = pn.pane.Markdown(md.spending_plot_info_md, style={"color": self.color_font}, width=1250, height=150,
                                sizing_mode="fixed", margin=(10,5,10,15))
        spending_plot_header = pn.Column(spending_plot_title, spending_plot_info, background=self.color_background, sizing_mode='stretch_height', width=1250)
        
        
        
        liquid_plot_filename = f"Assets/{self.name}'s Liquid Monte Carlo Plot.png"
        liquid_plot = pn.pane.PNG(liquid_plot_filename, sizing_mode="scale_both", align="center")
        liquid_plot_row = pn.Row(liquid_plot, background=self.color_background, width=1250)

        net_asset_plot = pn.pane.PNG(f"Assets/{self.name}'s Net Monte Carlo Plot.png", sizing_mode="scale_both", align="center")
        net_asset_plot_row = pn.Row(net_asset_plot, background=self.color_background, width=1250)


        # Put all elements together into one column
        dashboard = pn.Column(title, intro_info_row, growth_plot_header, 
                              growth_comparison_plot_row, spending_plot_header, liquid_stat_row, liquid_plot_row, net_stat_row, net_asset_plot_row, sizing_mode='stretch_height', background=self.color_background,
                                align='center', width=1250)

        # ## Requires Selenium and either a Chrome, Gecko, or Firefox driver in the PATH
        # Does not save properly as it they are 
        # pn.panel(dashboard).save('HSA and Portfolio Success Analysis.png')

        from bokeh.resources import INLINE
        
        if save_filename == None:
            pn.panel(dashboard).save('Assets/HSA_and_Portfolio_Success_Analysis.html', resources=INLINE)
        else:
            pn.panel(dashboard).save(f'Assets/{save_filename}.html', resources=INLINE)


        # Panel.save works to save .png files of your dashboard. But it requires Selenium and a chromedriver to be installed and in the PATH.
        dashboard.save('Assets/HSA_and_Portfolio_Success_Analysis.png')

        ### This can't work unless you have wkhtmltopdf installed on the computer
        # This is an .exe. more info can be found here http://wkhtmltopdf.org
        # import imgkit
        # config = imgkit.config(wkhtmltoimage=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe')
        # imgkit.from_file('Assets/HSA and Portfolio Success Analysis.html', 'Assets/out.jpg', config=config)

        return dashboard
    