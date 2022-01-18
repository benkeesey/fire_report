import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import holoviews as hv, panel as pn

class Plot_Vars(object):
    def __init__(self, **argd):
            self.__dict__.update(argd)
             
    def color_schemes(self):
           
        ### Color Schemes
        # Follows the following order:
        # 0-3 are the main colors
        # 4 is accent
        # 5 is an alternate color for accent
        # 6 is the background color
        # 7 is the font color 
        color_schemes_available = {
                                'office_pastel':('#b76e79', '#87907d', '#d2a9aa', '#b6c9b3', '#e1d1d1', '#d2a9aa', '#ffffff', '#535253'),
                                'mountain_range':('#a84729', '#456c3d', '#62341e', '#848a56', '#b3995b', '#d29057', '#b0bb9b', '#0F0F0F'),
                                'xerox':('#242424', '#494949', '#404048', '#282828', '#e2e6e6', '#b6b6b6', '#ffffff', '#000000'),
                                'stickies':('#f6114a', '#1fa2ff', '#3333ff', '#661fff', '#ddbea9', '#eb8258', '#ffffff', '#2d3047'),
                                'miami_sunrise':('#fb8500', '#5390d9', '#f8961e', '#f9c74f', '#f79d84', '#C8D7FF', '#FFF5D6', '#023047')
                                }
        if self.color_scheme in color_schemes_available:
            return color_schemes_available[self.color_scheme]
        else:
            import warnings
            warnings.warn("Warning! No valid color scheme picked, default selected.\nPlease pick from the following choices:\noffice_pastel\nmountain_range\nxerox\nstickies\nmiami_sunrise")
            return color_schemes_available['Deserted_6_color']
        
    def possible_starting_years(self):
        start_year = 1871
        end_year = 2022
        num_models_possible = (end_year-self.time_window)-start_year+2 # Have to add 2 to be inclusive of the end and start year 

        starting_years_list = []
        for i in range(num_models_possible):
            starting_years_list.append(start_year)
            start_year += 1
        return starting_years_list

        
    def model_account_returns_with_spending(self, inital_balance_dict, starting_year, yearly_market_df):

        # Create a copy of just the relevant years of Real_Return_Percentage based on the time range and the starting year
        model_return_data = yearly_market_df.loc[starting_year:starting_year+self.time_window-1, 'Real_Return_Percentage'].copy()

        year_range = list(np.arange(1,self.time_window+1))
        savings_remainder = self.Yearly_Savings
        ### DEPOSITS
        ### Calcuating HSA Contribution
        if self.Yearly_Savings//self.HSA_contribution_limit == 0:
            HSA_contribution = savings_remainder
            savings_remainder =- HSA_contribution
        else:
            HSA_contribution = self.HSA_contribution_limit
            savings_remainder =- self.HSA_contribution_limit

        ### Calcuating Roth Contribution
        # Have to calculate if savings is enough for pre-tax dollars
        if savings_remainder//(self.Roth_contribution_limit/(1-self.Marginal_Tax_Rate/100)) == 0:
            Roth_contribution = savings_remainder
            savings_remainder =- Roth_contribution
            # Roth is after tax dollars for contribution
            Roth_contribution = savings_remainder*(1-self.Marginal_Tax_Rate/100)
        else:
            Roth_contribution = self.Roth_contribution_limit
            savings_remainder =- (self.Roth_contribution_limit/(1-self.Marginal_Tax_Rate/100))

        ### Calcuating 401k Contribution
        if savings_remainder//self.Traditional_401k_contribution_limit == 0:
            Traditional_401k_contribution = savings_remainder
            savings_remainder =- Traditional_401k_contribution
        else:
            Traditional_401k_contribution = self.Traditional_401k_contribution_limit
            savings_remainder =- self.Traditional_401k_contribution_limit

        ### Calcuating Brokerage Contribution
        Brokerage_contribution = savings_remainder*(1-self.Marginal_Tax_Rate/100)

        # print(HSA_contribution, Roth_contribution, Traditional_401k_contribution, Brokerage_contribution)


        Brokerage_balance_over_time = []
        HSA_balance_over_time = []
        Trad_401k_balance_over_time = []
        Roth_balance_over_time = []

        Total_balance_over_time = []
        Total_Liquid_balance_over_time = []
        
        for i, percent in enumerate(model_return_data):
            # Stop adding Yearly_Savings if past retirement age
            # model_return_data corresponds with age of user. i.e. model_return_data[0] == age, model_return_data[1] == age+1 

            Brokerage_YB = inital_balance_dict['balance_Brokerage']
            HSA_YB = inital_balance_dict['balance_HSA']
            Traditional_401k_YB = inital_balance_dict['balance_401k']
            Roth_YB = inital_balance_dict['balance_Roth']

            ### Calcuating Withdrawls
            Brokerage_withdraw = self.retirement_spend
            HSA_withdraw = 0
            Traditional_401k_withdraw = 0
            Roth_withdraw = 0

            withdraw_remainder = 0


            if i >= self.retirement_age-self.age:

                for account in inital_balance_dict:
                    inital_balance_dict[account] = inital_balance_dict[account]*(1+percent/100)
                    inital_balance_dict[account] = inital_balance_dict[account]*(1-self.Expense_Ratio/100)

                inital_balance_dict['balance_HSA_qualified_expense'] = inital_balance_dict['balance_HSA_qualified_expense']+self.yearly_HSA_qualifed_expense

                Brokerage_Capital_Gains = inital_balance_dict['balance_Brokerage'] - Brokerage_YB
                if Brokerage_Capital_Gains < 0:
                    Brokerage_Capital_Gains = 0

                inital_balance_dict['balance_Brokerage'] = inital_balance_dict['balance_Brokerage'] - Brokerage_Capital_Gains*(self.Capital_Gains_Tax/100) # Remove the Captial Gains Tax

                # Remove retirement spend
                inital_balance_dict['balance_Brokerage'] = inital_balance_dict['balance_Brokerage']-Brokerage_withdraw
                if inital_balance_dict['balance_Brokerage'] < 0:
                    withdraw_remainder = abs(inital_balance_dict['balance_Brokerage'])
                    inital_balance_dict['balance_Brokerage'] = 0

                inital_balance_dict['balance_HSA'] = inital_balance_dict['balance_HSA']-(HSA_withdraw+withdraw_remainder)
                inital_balance_dict['balance_HSA_qualified_expense'] = inital_balance_dict['balance_HSA_qualified_expense']-(HSA_withdraw+withdraw_remainder)
                # Set HSA balance to zero if the withdraw amount was larger than the account balance
                if inital_balance_dict['balance_HSA'] < 0:
                    inital_balance_dict['balance_HSA'] = 0
                # Set HSA qualified expense balance to zero if the withdraw amount was larger than the account balance
                # This remainder is what is sent to the other accounts, as it is realistically the the only valid funds that can be removed.
                if inital_balance_dict['balance_HSA_qualified_expense'] < 0:
                    withdraw_remainder = abs(inital_balance_dict['balance_HSA_qualified_expense'])
                    inital_balance_dict['balance_HSA_qualified_expense'] = 0

                if i+self.age+1 > 59:
                    # Assume once qualified all assets are sold and taxed as income at once. (conservative assumption)
                    Trad_401k_Capital_Gains = inital_balance_dict['balance_401k'] - inital_balance_dict['balance_401k_contributions']
                    if Trad_401k_Capital_Gains < 0:
                        Trad_401k_Capital_Gains = 0

                    Trad_401k_Capital_Gains_tax = Trad_401k_Capital_Gains*(self.Retired_Capital_Gains_Tax/100)
                    Trad_401k_Deposits_tax = inital_balance_dict['balance_401k_contributions']*(self.Retired_Marginal_Tax_Rate/100)
                    inital_balance_dict['balance_401k'] = inital_balance_dict['balance_401k']-(Trad_401k_Capital_Gains_tax+Trad_401k_Deposits_tax)

                    inital_balance_dict['balance_401k'] = inital_balance_dict['balance_401k']-(Traditional_401k_withdraw+withdraw_remainder)
                    if inital_balance_dict['balance_401k'] < 0:
                        withdraw_remainder = abs(inital_balance_dict['balance_401k'])
                        inital_balance_dict['balance_401k'] = 0

                    inital_balance_dict['balance_Roth'] = inital_balance_dict['balance_Roth']-(Roth_withdraw+withdraw_remainder)
                    if inital_balance_dict['balance_Roth'] < 0:
                        withdraw_remainder = abs(inital_balance_dict['balance_Roth'])
                        inital_balance_dict['balance_Roth'] = 0                


            else:
                inital_balance_dict['balance_Brokerage'] = (inital_balance_dict['balance_Brokerage']+Brokerage_contribution)*(1+percent/100)
                inital_balance_dict['balance_HSA'] = (inital_balance_dict['balance_HSA']+HSA_contribution)*(1+percent/100)

                inital_balance_dict['balance_401k'] = (inital_balance_dict['balance_401k']+Traditional_401k_contribution)*(1+percent/100)
                inital_balance_dict['balance_Roth'] = (inital_balance_dict['balance_Roth']+Roth_contribution)*(1+percent/100)

                inital_balance_dict['balance_HSA_qualified_expense'] = inital_balance_dict['balance_HSA_qualified_expense']+self.yearly_HSA_qualifed_expense
                inital_balance_dict['balance_401k_contributions'] = inital_balance_dict['balance_401k_contributions']+Traditional_401k_contribution

                # Removing the Capital Gains Tax in Brokerage Account
                Brokerage_Capital_Gains = inital_balance_dict['balance_Brokerage'] - Brokerage_YB
                if Brokerage_Capital_Gains < 0:
                    Brokerage_Capital_Gains = 0

                inital_balance_dict['balance_Brokerage'] = inital_balance_dict['balance_Brokerage'] - Brokerage_Capital_Gains*(self.Capital_Gains_Tax/100) # Remove the Captial Gains Tax



            total_balance = inital_balance_dict['balance_Brokerage'] + inital_balance_dict['balance_HSA'] + inital_balance_dict['balance_401k'] + inital_balance_dict['balance_Roth']

            if i+self.age+1 > 59:
                total_liquid_balance = inital_balance_dict['balance_Brokerage'] + inital_balance_dict['balance_HSA_qualified_expense'] + inital_balance_dict['balance_401k'] + inital_balance_dict['balance_Roth']
            else:
                total_liquid_balance = inital_balance_dict['balance_Brokerage'] + inital_balance_dict['balance_HSA_qualified_expense']
            Brokerage_balance_over_time.append(inital_balance_dict['balance_Brokerage'])
            HSA_balance_over_time.append(inital_balance_dict['balance_HSA'])
            Trad_401k_balance_over_time.append(inital_balance_dict['balance_401k'])
            Roth_balance_over_time.append(inital_balance_dict['balance_Roth'])

            Total_balance_over_time.append(total_balance)
            Total_Liquid_balance_over_time.append(total_liquid_balance)

        # Brokerage_return = pd.Series(Brokerage_balance_over_time, index=year_range, name=starting_year)
        # HSA_return = pd.Series(HSA_balance_over_time, index=year_range, name=starting_year)
        # Trad_401k_return = pd.Series(Trad_401k_balance_over_time, index=year_range, name=starting_year)
        # Roth_return = pd.Series(Roth_balance_over_time, index=year_range, name=starting_year)

        Total_Net_Return_Spending = pd.Series(Total_balance_over_time, index=year_range, name=starting_year)
        Total_Liquid_Return_Spending = pd.Series(Total_Liquid_balance_over_time, index=year_range, name=starting_year)
        
        return Total_Net_Return_Spending, Total_Liquid_Return_Spending

    
    def spending_fire_plot(self, df, file_name):
        from matplotlib.ticker import StrMethodFormatter



        color_1 = self.color_schemes()[0]
        color_2 = self.color_schemes()[1]
        color_3 = self.color_schemes()[2]
        color_4 = self.color_schemes()[3]
        color_accent = self.color_schemes()[4]
        color_alt = self.color_schemes()[5]
        color_background = self.color_schemes()[6]
        color_font = self.color_schemes()[7]
        
        
        plt.figure(figsize=(25, 10), dpi=80)
        plt.ylabel('Balance Available')
        plt.xlabel('Years')
        plt.grid(visible=True, color=color_accent)

        ax = plt.gca()

        # X-Axis Formatting
        ax.set_facecolor(color_background)
        ax.xaxis.label.set_color(color_font)
        ax.tick_params(axis='x', colors=color_font)
        ax.set_xticks(np.arange(1, df.shape[1]+1, step=1), minor=False)
        # Y-Axis Formatting
        ax.yaxis.label.set_color(color_font)
        ax.tick_params(axis='y', colors=color_font)


        ax.axis(xmin=1,xmax=df.shape[1]+1, ymin=0, ymax=df.max().max())
        ax.ticklabel_format(axis='both', style='sci', scilimits=(1,10), useOffset=None, useLocale=None, useMathText=None)


        ax.yaxis.set_major_formatter(StrMethodFormatter('${x:,.0f}')) # No decimal places with dollar sign
        ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}')) # No decimal places with dollar sign

        plt.plot(df.T, color=color_accent)

        # Get the Average across all models
        mean_model = df.mean(axis=0)
        plt.plot(mean_model, linestyle='dashed', linewidth=5, color=color_1, label='Average Value')
        ax.legend(labelcolor=[color_1], loc='upper left', edgecolor=color_font, facecolor=color_background)

        # Annotate the Average line
        num = mean_model.iloc[-1].round(0)
        currency_string = "Average\nEnding\nBalance:\n${:,.0f}".format(num)
        plt.annotate(currency_string, (df.shape[1]+.1,num), color=color_1, verticalalignment='center')

        # plt.show()
        if file_name is None:
            file_name=f"{self.Name}'s' Monte Carlo Plot"
        plt.savefig(f'{file_name}.png', dpi=80, facecolor=color_background, bbox_inches='tight', pad_inches=0)
    
    
    def Monte_Carlo_Plot_Spending(self, yearly_market_df):
        total_liquid_assets_df = pd.DataFrame()
        total_net_assets_df = pd.DataFrame()
        for starting_year in self.possible_starting_years():
            # Need to create new dict with inital variables as these get changed and updated as model runs for each possible starting year.
            inital_balance_dict = {'balance_Brokerage':self.balance_Brokerage, 'balance_HSA':self.balance_HSA, 'balance_401k':self.balance_401k, 'balance_Roth':self.balance_Roth, 'balance_HSA_qualified_expense':self.balance_HSA_qualified_expense, 'balance_401k_contributions':self.balance_401k_contributions}

            Total_Net_Return_Spending, Total_Liquid_Return_Spending = self.model_account_returns_with_spending(inital_balance_dict, starting_year, yearly_market_df)

            total_liquid_assets_df = total_liquid_assets_df.append(Total_Liquid_Return_Spending)
            total_net_assets_df = total_net_assets_df.append(Total_Net_Return_Spending)

        self.Total_Net_Return_Spending_df = total_net_assets_df
        self.Total_Liquid_Return_Spending_df = total_liquid_assets_df

        self.spending_fire_plot(df=total_net_assets_df, file_name=f"Assets/{self.Name}'s Net Monte Carlo Plot")
        self.spending_fire_plot(df=total_liquid_assets_df, file_name=f"Assets/{self.Name}'s Liquid Monte Carlo Plot")
        
    ###########################################################################################################
    # Modeling Just Growth of Accounts
    ###########################################################################################################
    def model_brokerage_returns(self, yearly_market_df, starting_year):
        # Create a copy of just the relevant years of Real_Return_Percentage based on the time range and the starting year
        model_return_data = yearly_market_df.loc[starting_year:starting_year+self.time_window-1, 'Real_Return_Percentage'].copy()

        year_range = list(np.arange(1,self.time_window+1))

        after_tax_yearly_investment = self.Yearly_Savings*(1-self.Marginal_Tax_Rate/100)
        YB_balance = self.starting_balance
        deposit_balance = self.starting_balance
        liquid_balance = self.starting_balance

        ### Brokerage Account
        balance_over_time = []
        deposit_balance_over_time = []
        liquid_balance_over_time = []
        for i, percent in enumerate(model_return_data): 
            # Stop adding Yearly_Savings if past retirement age
            # model_return_data corresponds with age of user. i.e. model_return_data[0] == age, model_return_data[1] == age+1 
            if i >= self.retirement_age-self.age:
                deposit_balance = deposit_balance
                YE_balance = (YB_balance)*(1+percent/100)
                # Calculate the dollars gained each year that would need to be taxed as capital gains. Assumes yearly selling and reinvestment of gains (conservative assumption)
                Brokerage_Capital_Gains = YE_balance - (YB_balance)
            else:
                deposit_balance = deposit_balance+after_tax_yearly_investment
                YE_balance = (YB_balance+after_tax_yearly_investment)*(1+percent/100)
                # Calculate the dollars gained each year that would need to be taxed as capital gains. Assumes yearly selling and reinvestment of gains (conservative assumption)
                Brokerage_Capital_Gains = YE_balance - (YB_balance+after_tax_yearly_investment)

            deposit_balance_over_time.append(deposit_balance) # Keep track of contribution balance

            if Brokerage_Capital_Gains < 0:
                Brokerage_Capital_Gains = 0

            YE_balance = YE_balance - Brokerage_Capital_Gains*(self.Capital_Gains_Tax/100) # Remove the Captial Gains Tax
            YE_balance = YE_balance*(1-self.Expense_Ratio/100) # Remove expense ratio from YE balance
            balance_over_time.append(YE_balance)
            YB_balance = YE_balance
            # Append balance of liquid assets (100% of assets after tax)
            liquid_balance = YE_balance
            liquid_balance_over_time.append(liquid_balance)
    
        net_return = pd.Series(balance_over_time, index=year_range, name=starting_year)
        liquid_balance = pd.Series(liquid_balance_over_time, index=year_range, name=starting_year)

        return net_return, liquid_balance


    def model_HSA_returns(self, yearly_market_df, starting_year):
        # 2022 deposit limit is $3600. Model assumes this is added in total at start of year
        # Create a copy of just the relevant years of Real_Return_Percentage based on the time range and the starting year
        model_return_data = yearly_market_df.loc[starting_year:starting_year+self.time_window-1, 'Real_Return_Percentage'].copy()

        year_range = list(np.arange(1,self.time_window+1))

        YB_balance = self.starting_balance # Year Begin balance. Starts with just the beginning account value
        liquid_balance = 0
        deposit_balance = self.starting_balance

        ### HSA Account
        balance_over_time = []
        deposit_balance_over_time = []
        liquid_balance_over_time = []

        for i, percent in enumerate(model_return_data):
            # Stop adding Yearly_Savings if past retirement age
            # model_return_data corresponds with age of user. i.e. model_return_data[0] == age, model_return_data[1] == age+1 
            if i >= self.retirement_age-self.age:
                deposit_balance = deposit_balance
                YE_balance = (YB_balance)*(1+percent/100)
            else:
                deposit_balance = deposit_balance+self.Yearly_Savings
                YE_balance = (YB_balance+self.Yearly_Savings)*(1+percent/100)

            deposit_balance_over_time.append(deposit_balance) # Keep track of contribution balance


            YE_balance = YE_balance*(1-self.Expense_Ratio/100)
            balance_over_time.append(YE_balance)
            YB_balance = YE_balance
            liquid_balance = liquid_balance+self.yearly_HSA_qualifed_expense
            liquid_balance_over_time.append(liquid_balance)

        net_return = pd.Series(balance_over_time, index=year_range, name=starting_year)
        liquid_balance = pd.Series(liquid_balance_over_time, index=year_range, name=starting_year)

        return net_return, liquid_balance

    def model_roth_returns(self, yearly_market_df, starting_year):
        # Create a copy of just the relevant years of Real_Return_Percentage based on the time range and the starting year
        model_return_data = yearly_market_df.loc[starting_year:starting_year+self.time_window-1, 'Real_Return_Percentage'].copy()

        year_range = list(np.arange(1,self.time_window+1))

        after_tax_yearly_investment = self.Yearly_Savings*(1-self.Marginal_Tax_Rate/100) # Roth Contributions are paid with after tax dollars
        YB_balance = self.starting_balance # Year Begin balance. Starts with just the beginning account value
        liquid_balance = 0
        deposit_balance = self.starting_balance

        ### 401k Roth Account
        balance_over_time = []
        deposit_balance_over_time = []
        liquid_balance_over_time = []
        
        for i, percent in enumerate(model_return_data):
            # Stop adding after_tax_yearly_investment if past retirement age
            # model_return_data corresponds with age of user. i.e. model_return_data[0] == age, model_return_data[1] == age+1 
            if i >= self.retirement_age-self.age:
                deposit_balance = deposit_balance
                YE_balance = (YB_balance)*(1+percent/100)
            else:
                deposit_balance = deposit_balance+after_tax_yearly_investment
                YE_balance = (YB_balance+after_tax_yearly_investment)*(1+percent/100)

            deposit_balance_over_time.append(deposit_balance) # Keep track of contribution balance

            YE_balance = YE_balance*(1-self.Expense_Ratio/100)
            balance_over_time.append(YE_balance)
            YB_balance = YE_balance

            if i+self.age+1 > 59:
                liquid_balance = YE_balance

            liquid_balance_over_time.append(liquid_balance)

        net_return = pd.Series(balance_over_time, index=year_range, name=starting_year)
        liquid_balance = pd.Series(liquid_balance_over_time, index=year_range, name=starting_year)

        return net_return, liquid_balance

    def model_trad_401k_returns(self, yearly_market_df, starting_year):
        # Create a copy of just the relevant years of Real_Return_Percentage based on the time range and the starting year
        model_return_data = yearly_market_df.loc[starting_year:starting_year+self.time_window-1, 'Real_Return_Percentage'].copy()

        year_range = list(np.arange(1,self.time_window+1))

        YB_balance = self.starting_balance # Year Begin balance. Starts with just the beginning account value
        liquid_balance = 0
        deposit_balance = self.starting_balance

        ### 401k Account
        balance_over_time = []
        deposit_balance_over_time = []
        liquid_balance_over_time = []

        for i, percent in enumerate(model_return_data):
            # Stop adding Yearly_Savings if past retirement age
            # model_return_data corresponds with age of user. i.e. model_return_data[0] == age, model_return_data[1] == age+1 
            if i >= self.retirement_age-self.age:
                deposit_balance = deposit_balance
                YE_balance = (YB_balance)*(1+percent/100)
            else:
                deposit_balance = deposit_balance+self.Yearly_Savings
                YE_balance = (YB_balance+self.Yearly_Savings)*(1+percent/100)

            deposit_balance_over_time.append(deposit_balance) # Keep track of contribution balance

            YE_balance = YE_balance*(1-self.Expense_Ratio/100)
            balance_over_time.append(YE_balance)
            YB_balance = YE_balance

            # Assets are not liquid until after user turns over 59 years old in a 401k account
            # Assets are then taxed as income at the now retired persons tax rates
            if i+self.age+1 > 59:
                liquid_capital_gains = (YE_balance-deposit_balance)*(1-self.Retired_Capital_Gains_Tax/100)
                liquid_deposits = deposit_balance*(1-self.Retired_Marginal_Tax_Rate/100)
                liquid_balance = liquid_capital_gains+liquid_deposits


            liquid_balance_over_time.append(liquid_balance)

        net_return = pd.Series(balance_over_time, index=year_range, name=starting_year)
        liquid_balance = pd.Series(liquid_balance_over_time, index=year_range, name=starting_year)

        return net_return, liquid_balance


    def Monte_Carlo_Growth_Models(self, account_type, yearly_market_df):
        ### Model all the possible returns for every possible time window
        df = pd.DataFrame()
        liquid_df = pd.DataFrame()

        if account_type == 'HSA':
            for starting_year in self.possible_starting_years():
                net_return, liquid_balance = self.model_HSA_returns(yearly_market_df, starting_year)
                # plt.plot(net_return, color=global_color_scheme[color_alt])
                df = df.append(net_return)
                liquid_df = liquid_df.append(liquid_balance)
            
            # Transpose DataFrames for easier plotting
            df = df.T
            liquid_df = liquid_df.T
            # Save DataFrames as objects associated with Class object
            self.HSA_models_df = df
            self.HSA_models_liquid_df = liquid_df
            
        elif account_type == 'Roth':
            for starting_year in self.possible_starting_years():
                net_return, liquid_balance = self.model_roth_returns(yearly_market_df, starting_year)
                # plt.plot(net_return, color=global_color_scheme[color_alt])
                df = df.append(net_return)
                liquid_df = liquid_df.append(liquid_balance)
                
            # Transpose DataFrames for easier plotting
            df = df.T
            liquid_df = liquid_df.T
            # Save DataFrames as objects associated with Class object
            self.Roth_models_df = df
            self.Roth_models_liquid_df = liquid_df
            
        elif account_type == 'Trad_401k':
            for starting_year in self.possible_starting_years():
                net_return, liquid_balance = self.model_trad_401k_returns(yearly_market_df, starting_year)
                # plt.plot(net_return, color=global_color_scheme[color_alt])
                df = df.append(net_return)
                liquid_df = liquid_df.append(liquid_balance)
                
            # Transpose DataFrames for easier plotting
            df = df.T
            liquid_df = liquid_df.T
            # Save DataFrames as objects associated with Class object
            self.Trad_401k_models_df = df
            self.Trad_401k_models_liquid_df = liquid_df
            
        elif account_type == 'Brokerage':
            for starting_year in self.possible_starting_years():
                net_return, liquid_balance = self.model_brokerage_returns(yearly_market_df, starting_year)
                # plt.plot(net_return, color=global_color_scheme[color_alt])
                df = df.append(net_return)
                liquid_df = liquid_df.append(liquid_balance)
                
            # Transpose DataFrames for easier plotting
            df = df.T
            liquid_df = liquid_df.T
            # Save DataFrames as objects associated with Class object
            self.Brokerage_models_df = df
            self.Brokerage_models_liquid_df = liquid_df
            
        else:
            raise ValueError('Account type parameter was not one of following strings in list: ["HSA", "Roth", "Trad_401k", "Brokerage"]')

        return df, liquid_df


    def Monte_Carlo_Plot_Growth_Comparison(self, yearly_market_df):
        from matplotlib.ticker import StrMethodFormatter

        # Get Growth Data from various types of accounts
        HSA_models_df, HSA_models_liquid_df = self.Monte_Carlo_Growth_Models('HSA', yearly_market_df)
        Roth_models_df, Roth_models_liquid_df = self.Monte_Carlo_Growth_Models('Roth', yearly_market_df)
        Trad_401k_models_df, Trad_401k_models_liquid_df = self.Monte_Carlo_Growth_Models('Trad_401k', yearly_market_df)
        Brokerage_models_df, Brokerage_models_liquid_df = self.Monte_Carlo_Growth_Models('Brokerage', yearly_market_df)
        
        # Getting color palette information
        color_1 = self.color_schemes()[0]
        color_2 = self.color_schemes()[1]
        color_3 = self.color_schemes()[2]
        color_4 = self.color_schemes()[3]
        color_accent = self.color_schemes()[4]
        color_alt = self.color_schemes()[5]
        color_background = self.color_schemes()[6]
        color_font = self.color_schemes()[7]
        
        # Start of Matplotlib Figure
        plt.figure(figsize=(25, 10), dpi=80)
        plt.ylabel('Balance Available')
        plt.xlabel('Years')
        plt.grid(visible=True, color=color_accent)

        ax = plt.gca()

        # X-Axis Formatting
        ax.set_facecolor(color_background)
        ax.xaxis.label.set_color(color_font)
        ax.tick_params(axis='x', colors=color_font)
        
        max_xaxis_val = max([HSA_models_df.shape[0], Roth_models_df.shape[0], Trad_401k_models_df.shape[0], Brokerage_models_df.shape[0]])
        max_yaxis_val = max(HSA_models_df.max().max(), Roth_models_df.max().max(), Trad_401k_models_df.max().max(), Brokerage_models_df.max().max())
        
        ax.set_xticks(np.arange(1, (max_xaxis_val)+1, step=1), minor=False)
        # Y-Axis Formatting
        ax.yaxis.label.set_color(color_font)
        ax.tick_params(axis='y', colors=color_font)

        
        ax.axis(xmin=1,xmax=max_xaxis_val+1, ymin=0, ymax=max_yaxis_val)
        ax.ticklabel_format(axis='both', style='sci', scilimits=(1,10), useOffset=None, useLocale=None, useMathText=None)


        ax.yaxis.set_major_formatter(StrMethodFormatter('${x:,.0f}')) # No decimal places with dollar sign
        ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}')) # No decimal places with dollar sign

        plt.plot(HSA_models_df, color=color_accent)
        plt.plot(Brokerage_models_df, color=color_alt)
        # TODO: Include the other accounts in this comparison
        # plt.plot(Roth_models_df, color=color_alt)
        # plt.plot(Trad_401k_models_df, color=color_alt)

        # Get the HSA average across all models
        HSA_Mean_Model = HSA_models_df.mean(axis=1)
        plt.plot(HSA_Mean_Model, linestyle='dashed', linewidth=5, color=color_1, label='HSA Model')

        # Annotate the HSA Average line
        num = HSA_Mean_Model.iloc[-1].round(0)
        currency_string = "Average HSA\nEnding\nBalance:\n${:,.0f}".format(num)
        plt.annotate(currency_string, (self.time_window+.1,num), color=color_1, verticalalignment='center')

        # Get the Brokerage average across all models
        Brokerage_Mean_Model = Brokerage_models_df.mean(axis=1)
        plt.plot(Brokerage_Mean_Model, linestyle='dashed', linewidth=5, color=color_2, label='Brokerage Model')

        # Annotate the Brokerage Average line
        num = Brokerage_Mean_Model.iloc[-1].round(0)
        currency_string = "Average Brokerage\nEnding\nBalance:\n${:,.0f}".format(num)
        plt.annotate(currency_string, (self.time_window+.1,num), color=color_2, verticalalignment='center')


        # Cash investment, showing just yearly savings
        # Cash Contributions are also made after tax. Yearly Savings in based of a Gross number
        after_tax_yearly_investment = self.Yearly_Savings*(1-self.Marginal_Tax_Rate/100)

        deposits_before_retirement = np.arange(start=after_tax_yearly_investment, stop=after_tax_yearly_investment*(self.retirement_age-self.age+1), step=after_tax_yearly_investment)
        deposits_after_retirement = np.linspace(deposits_before_retirement[-1], deposits_before_retirement[-1], num=self.time_window-(self.retirement_age-self.age))
        deposit_balance = np.concatenate([deposits_before_retirement,deposits_after_retirement])

        plt.plot(np.arange(1,self.time_window+1), deposit_balance, linestyle='dotted', linewidth=5, color=color_3, label='Cash Savings')
        ax.legend(labelcolor=[color_1, color_2, color_3], loc='upper left', edgecolor=color_font, facecolor=color_background)

        # Annotate the Cash Ending Balance
        num = deposit_balance[-1]
        currency_string = "Cash\nEnding\nBalance:\n${:,.0f}".format(num)
        plt.annotate(currency_string, (self.time_window+.5,num), color=color_3, verticalalignment='center')
        # Save Matplotlib figure as png file in Assets folder
        plt.savefig('Assets/Monte_Carlo_Plot_Growth_Comparison.png', dpi=80, facecolor=color_background, bbox_inches='tight', pad_inches=0)


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
        sucessful_models = df.all(axis=1).value_counts()[True]
        # Not used but could be to calculate the failure percentage
        failed_models = df.all(axis=1).value_counts()[False]

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



    def Dashboard(self, save_html=False, save_filename=None):
        """
        Returns a simple static dashboard as an Panel object.
        One column with multiple rows for relevant headers, Text, and Visuals
        """
        
        
        # Get color information from the color palette 
        color_1 = self.color_schemes()[0]
        color_2 = self.color_schemes()[1]
        color_3 = self.color_schemes()[2]
        color_4 = self.color_schemes()[3]
        color_accent = self.color_schemes()[4]
        color_alt = self.color_schemes()[5]
        color_background = self.color_schemes()[6]
        color_font = self.color_schemes()[7]
        
        # Header text for the static Dashboard
        header = pn.pane.Markdown("# **<ins>HSA and Portfolio Success Analysis</ins>**", style={"color": color_font}, width=500, 
                            sizing_mode="stretch_width", margin=(10,5,10,15))

        icon1 = pn.pane.PNG("fire.png",
                        height=60, sizing_mode="fixed", align="center")

        icon2 = pn.pane.PNG("stock-market.png", 
                        height=60, sizing_mode="fixed", align="center")

        # Put together title in a panel Row
        title = pn.Row(header, pn.Spacer(), icon1, icon2, background=color_background, sizing_mode='fixed', width=1250, height=70)

        # Intro paragraph giving information about the report
        intro_info = pn.pane.Markdown("""
        ### The following information is helps visualize possible retirement scenarios using the idea that future returns will likley fall between the best and worst historical returns. This analysis is heavely influenced by the FIRE movement and [<ins>FIRECalc</ins>](https://www.firecalc.com/).
        ### The largest addition of this report is the idea of having a mixture of tax advantage accounts (HSA, Traditional 401k, and Roth) in addition to Brokerage accounts that offer different tax benefits. The report follows the following funding and withdraw strategies:
        * #### Funding Order Strategy: **HSA --> Roth --> Tradtional 401k --> Brokerage**
        * #### Withdraw Order Strategy: **Brokerage Accounts --> HSA --> Traditonal 401k --> Roth**

        #### The following plots and statistics should be interpreted in aggregate as they represent what you returns would have been in historical markets adjusted in current real dollars (i.e. what would your account balances been if you started investing in 1975, 1976, etc.)

        ##### Note: Historical data is taken from [Robert Shiller](http://www.econ.yale.edu/~shiller/) where he offers his [U.S. Stock Markets 1871-Present and CAPE Ratio.](http://www.econ.yale.edu/~shiller/data.htm) dataset.

        """, style={"color": color_font}, width=1250, height =300,
                                sizing_mode="scale_both", margin=(10,5,10,15))

        intro_info_row = pn.Row(intro_info, background=color_background, sizing_mode='fixed', width=1250, height=300)

        # Call Statistic function to get values to show in Dashboard
        # Show Statistics for Liquid Assets 
        success_percentage, final_first_quartile, final_median, final_third_quartile = self.Monte_Carlo_Plot_Spending_Statistics(self.Total_Liquid_Return_Spending_df)
        # Create Markdown Text fields of the statistics to show in Dashboard
        # Change the values to show in the correct currency string format
        final_first_quartile_str = "${:,.0f}".format(self.final_first_quartile)
        final_median_str = "${:,.0f}".format(self.final_median)
        final_third_quartile_str = "${:,.0f}".format(self.final_third_quartile)
        

        liquid_stat1 = pn.pane.Markdown(f"### Successful Models:", style={"color": color_font}, height=70, 
                        sizing_mode="stretch_width", margin=(10,0,10,15), align='center')
        liquid_stat1_val = pn.pane.Markdown(f"# {success_percentage}%", style={"color": color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,5,10,0), align='center')
        
        liquid_stat2 = pn.pane.Markdown(f"#### Ending 25% Quantile Portfolio Balance:", style={"color": color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,0,10,15), align='center')
        liquid_stat2_val = pn.pane.Markdown(f"#{final_first_quartile_str}", style={"color": color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,15,10,0), align='center')

        liquid_stat3 = pn.pane.Markdown(f"#### Ending 75% Quantile Portfolio Balance:", style={"color": color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,0,10,15), align='center')
        liquid_stat3_val = pn.pane.Markdown(f"#{final_third_quartile_str}", style={"color": color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,15,10,0), align='center')

        liquid_stat_row = pn.Row(liquid_stat1, liquid_stat1_val, liquid_stat2, liquid_stat2_val, liquid_stat3, liquid_stat3_val, background=color_background, sizing_mode='fixed', width=1250, height=70)
        
        # Show Statistics for Net Assets 
        success_percentage, final_first_quartile, final_median, final_third_quartile = self.Monte_Carlo_Plot_Spending_Statistics(self.Total_Net_Return_Spending_df)
        # Create Markdown Text fields of the statistics to show in Dashboard
        # Change the values to show in the correct currency string format
        final_first_quartile_str = "${:,.0f}".format(self.final_first_quartile)
        final_median_str = "${:,.0f}".format(self.final_median)
        final_third_quartile_str = "${:,.0f}".format(self.final_third_quartile)
        

        net_stat1 = pn.pane.Markdown(f"### Sucessful Models:", style={"color": color_font}, height=70, 
                        sizing_mode="stretch_width", margin=(10,0,10,15), align='center')
        net_stat1_val = pn.pane.Markdown(f"# {success_percentage}%", style={"color": color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,5,10,0), align='center')
        
        net_stat2 = pn.pane.Markdown(f"#### Ending 25% Quantile Portfolio Balance:", style={"color": color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,0,10,15), align='center')
        net_stat2_val = pn.pane.Markdown(f"#{final_first_quartile_str}", style={"color": color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,15,10,0), align='center')

        net_stat3 = pn.pane.Markdown(f"#### Ending 75% Quantile Portfolio Balance:", style={"color": color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,0,10,15), align='center')
        net_stat3_val = pn.pane.Markdown(f"#{final_third_quartile_str}", style={"color": color_font}, height=70, 
                                sizing_mode="stretch_width", margin=(10,15,10,0), align='center')

        net_stat_row = pn.Row(net_stat1, net_stat1_val, net_stat2, net_stat2_val, net_stat3, net_stat3_val, background=color_background, sizing_mode='fixed', width=1250, height=70)



        # Growth Plot Header Creation
        growth_plot_title = pn.pane.Markdown("# <ins>HSA, Brokerage, and Cash Accounts Growth Comparison</ins>", style={"color": color_font}, 
                        sizing_mode="fixed", margin=(10,5,5,15), width=1250, height=50)
        growth_plot_account_info = pn.pane.Markdown("""
        ### This plot shows Monte Carlo simulated growths of different account types with same input parameters:

        * #### HSA: Health Savings Account deposits are pre-tax, growth and withdraws are not taxed as long as they have a receipt for a qualified medical expense 
        * #### Brokerage: Regular Investment Account. Contributions are after tax and Capital Gains are taxed.
        * #### Cash Deposits: Just tracking deposits (after tax) with no investment. Note that after retirement deposits stop.

        #### Each faint line represents one possible modeled year of growth for a specifc historic time range. The larger dashed lines are the average account values for each account type. The blue dotted line is the tracking the after tax cash deposits made.
        """, style={"color": color_font}, width=1250, sizing_mode="scale_both", margin=(10,5,10,15))
        
        growth_plot_header = pn.Column(growth_plot_title, growth_plot_account_info, background=color_background, sizing_mode='fixed', width=1250, height=300)
        
        growth_comparison_plot = pn.pane.PNG("Assets/Monte_Carlo_Plot_Growth_Comparison.png", sizing_mode="scale_both", align="center")
        growth_comparison_plot_row = pn.Row(growth_comparison_plot, background=color_background, width=1250)

        # FIRE Spending Plot Header Creation
        spending_plot_title = pn.pane.Markdown("# <ins>FIRE (Financial Independence, Retire Early) Plot:</ins>", style={"color": color_font}, width=500, height=50, 
                        sizing_mode="stretch_width", margin=(10,5,10,15))
        spending_plot_info = pn.pane.Markdown("""
        ### These plots shows Monte Carlo simulated growths of all your account parameters and retirement age and spending.

        #### There are two plots: the Liquid and Net Asset plots. They are functionally the same but the Liquid Asset plot shows just liquid assets (i.e. You are only able to withdraw qualified medical expenses from an HSA without receiving a large fine.) Each faint line represents one possible modeled year of growth for a specifc historic time range. The larger dashed line is the average account value over time. 
        #### The additonal statistics help show the the number of sucessful models (any models that never had a 0 total account balance) as well as the 25% and 75% quantile ending balance.

        """, style={"color": color_font}, width=1250, height=150,
                                sizing_mode="fixed", margin=(10,5,10,15))
        spending_plot_header = pn.Column(spending_plot_title, spending_plot_info, background=color_background, sizing_mode='stretch_height', width=1250)
        
        
        
        liquid_plot_filename = f"Assets/{self.Name}'s Liquid Monte Carlo Plot.png"
        liquid_plot = pn.pane.PNG(liquid_plot_filename, sizing_mode="scale_both", align="center")
        liquid_plot_row = pn.Row(liquid_plot, background=color_background, width=1250)

        net_asset_plot = pn.pane.PNG(f"Assets/{self.Name}'s Net Monte Carlo Plot.png", sizing_mode="scale_both", align="center")
        net_asset_plot_row = pn.Row(net_asset_plot, background=color_background, width=1250)


        # Put all elements together into one column
        dashboard = pn.Column(title, intro_info_row, growth_plot_header, 
                              growth_comparison_plot_row, spending_plot_header, liquid_stat_row, liquid_plot_row, net_stat_row, net_asset_plot_row, sizing_mode='stretch_height', background='#4c566a',
                                align='center', width=1250)

        # ## Requires Selenium and either a Chrome, Gecko, or Firefox driver in the PATH
        # Does not save properly as it they are 
        # pn.panel(dashboard).save('HSA and Portfolio Success Analysis.png')

        from bokeh.resources import INLINE
        
        if save_filename == None:
            pn.panel(dashboard).save('Assets/HSA and Portfolio Success Analysis.html', resources=INLINE)
        else:
            pn.panel(dashboard).save(f'Assets/{save_filename}.html', resources=INLINE)

        return dashboard
        # ### This can't work unless you have wkhtmltopdf installed on the computer
        # # This is an .exe. more info can be found here http://wkhtmltopdf.org
        # import imgkit
        # imgkit.from_file('test.html', 'out.jpg')
    
    
    
def historical_market_data():
    market_data_df = pd.read_csv(r'C:\Users\bkeesey\Downloads\ie_Data.csv', header=7)
    market_data_df = market_data_df.dropna(axis=1, how='all').dropna(axis=0, how='all')
    market_data_df = market_data_df.loc[market_data_df['Date'].notna()].copy()
    
    data_col_names = [
    'Date',
    'S&P_Comp_P',
    'Dividend',
    'Earnings',
    'CPI',
    'Date_Fraction',
    'Long_Interest_Rate_GS10',
    'Real_Price',
    'Real_Dividend',
    'Real_Total_Return_Price',
    'Real_Earnings',
    'Real_TR_Scaled_Earnings ',
    'CAPE',
    'TR_CAPE',
    'CAPE_Yield',
    'Monthly_Total_Bond_Returns',
    'Real_Total_Bond_Returns',
    '10_Year_Annualized_Stock_Real_Return',
    '10_Year_Annualized_Bond_Real_Return',
    'Real_10_Year_Excess_Annualized_Returns']
    
    market_data_df.columns = data_col_names
    market_data_df['Year'] = market_data_df['Date'].apply(np.floor).astype(int)
    market_data_df['Real_Total_Return_Price'] = market_data_df['Real_Total_Return_Price'].str.strip().str.replace(',','').astype(float)
    
    # Calculate the monthly returns. Currently only implementing the yearly returns, but this could be used to increase model resolution.
    market_data_df['Real_Monthly_Return'] = market_data_df['Real_Total_Return_Price'].diff()
    market_data_df['Real_Monthly_Return_Percentage'] = (market_data_df['Real_Monthly_Return']/market_data_df['Real_Total_Return_Price'])*100
    
    yearly_market_df = pd.DataFrame()
    yearly_market_df['start_Real_Price'] = market_data_df.groupby('Year')['Real_Total_Return_Price'].first()
    yearly_market_df['end_Real_Price'] = market_data_df.groupby('Year')['Real_Total_Return_Price'].last()
    yearly_market_df['Real_Return_Percentage'] = ((yearly_market_df['end_Real_Price'] - yearly_market_df['start_Real_Price'])/yearly_market_df['start_Real_Price'])*100
    
    return yearly_market_df


def main(person_vars=None):
    
    """
    person_vars parameters:
    
    Yearly_Savings = Yearly Savings you plan to contribute to your accounts. NOTE: This is a Gross amount before tax.
    starting_balance = starting balance used in the (apples to apples) comparison of showing growth between accounts and cash investment.
    time_window = time in years you want to model. Years spend contributing and withdrawing from accounts is calculated using your current age and your retirement age within this time window
    yearly_HSA_qualifed_expense = Yearly estimate of qualifing HSA medical expenses. These will be treated as dollars you are able to withdraw without penalty from the HSA account. (currently this is just a static yearly value)
    age = The current age of the person
    retirement_age = The age the person plans of retiring. At this age they will stop contributing to their accounts and start withdrawing from them instead as spending.
    retirement_spend = Value person plans on spending per year in retirement (All calculated values are in Current Real Dollars.)

    balance_Brokerage = Currently balance in Brokerage accounts. Used in combined Liquid & Net worth Monte Carlo Plots
    balance_401k = Currently balance in Traditional 401k accounts. Used in combined Liquid & Net worth Monte Carlo Plots
    balance_HSA = Currently balance in HSA accounts. Used in combined Liquid & Net worth Monte Carlo Plots
    balance_Roth = Currently balance in Roth 401k accounts. Used in combined Liquid & Net worth Monte Carlo Plots 

    balance_HSA_qualified_expense = Currently balance of qualified medical expenses in HSA accounts. Used in combined Liquid & Net worth Monte Carlo Plots
    balance_401k_contributions = Currently balance of contributions made to Traditonal 401k accounts.This is needed to help calculate the Capital Gains tax once retirement age is reached. Deposits need to be taken into account that were already made. Used in combined Liquid & Net worth Monte Carlo Plots
                                NOTE: This should be 0 if balance_401k is also 0.
    """
    
    # Get Historical yearly market data
    # TODO: SQL connection to mySQL?
    yearly_market_df = historical_market_data()
    
    
    
    if person_vars == None:
        personal_finance_vars = {'Name':'Ben', 'Yearly_Savings' : 10000, 'starting_balance' : 0, 'time_window': 50, 'yearly_HSA_qualifed_expense':3000, 'age': 27, 'retirement_age':50, 'retirement_spend':90000,
                         'balance_Brokerage':1300000, 'balance_HSA':10000, 'balance_401k':130000, 'balance_Roth':30000, 'balance_HSA_qualified_expense':3000, 'balance_401k_contributions':10000}
        
        static_finance_vars = {'HSA_contribution_limit': 3600, 'Roth_contribution_limit': 6000
                        ,'Traditional_401k_contribution_limit': 20500, 'Roth_contribution_limit': 6000
                        ,'Expense_Ratio': .1, 'Marginal_Tax_Rate': 32, 'Capital_Gains_Tax': 15, 'Retired_Marginal_Tax_Rate': 24
                        ,'Retired_Capital_Gains_Tax': 15, 'color_scheme':'stickies'}
        Main_Plot = Plot_Vars(**{**static_finance_vars, **personal_finance_vars})
    else:
        Main_Plot = Plot_Vars(**person_vars)
    
    print(os.getcwd())
    Main_Plot.Monte_Carlo_Plot_Growth_Comparison(yearly_market_df)
    Main_Plot.Monte_Carlo_Plot_Spending(yearly_market_df)
    print('Finished Calculations')
    Main_Plot.Dashboard()
    print('Finished Successfully!')
    # print(Main_Plot.HSA_models_df)
    
    
if __name__ == "__main__":
    main()