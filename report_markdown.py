header_md = "# **<ins>HSA and Portfolio Success Analysis</ins>**"

intro_info_md = """
        ### The following information helps visualize possible retirement scenarios using the idea that future returns will likley fall between the best and worst historical returns. This analysis is heavily influenced by [<ins>FIRECalc</ins>](https://www.firecalc.com/).
        ### The largest addition of this report a mixture of tax advantage accounts (HSA, Traditional 401k, and Roth) in addition to Brokerage accounts that offer different tax benefits. The report follows the following funding and withdraw strategies:
        * #### Funding Order Strategy: **HSA --> Roth --> Tradtional 401k --> Brokerage**
        * #### Withdraw Order Strategy: **Brokerage Accounts --> HSA --> Traditonal 401k --> Roth**

        #### The following plots and statistics should be interpreted in aggregate as they represent what you returns would have been in historical markets adjusted in current real dollars (i.e. what would your account balances been if you started investing in 1975, 1976, etc.)

        ##### Note: Historical data is taken from [Robert Shiller](http://www.econ.yale.edu/~shiller/) where he offers his [U.S. Stock Markets 1871-Present and CAPE Ratio.](http://www.econ.yale.edu/~shiller/data.htm) dataset.

        """

growth_plot_title_md = "# <ins>HSA, Brokerage, and Cash Accounts Growth Comparison</ins>"

growth_plot_account_info_md = """
        ### This plot shows growths of different account types with same input parameters:

        * #### HSA: Health Savings Account deposits are pre-tax, growth and withdraws are not taxed as long as they have a receipt for a qualified medical expense 
        * #### Brokerage: Regular Investment Account. Contributions are after tax and Capital Gains are taxed.
        * #### Cash Deposits: Tracking deposits (after tax) with no investment. Note that after retirement deposits stop.

        #### Each faint line represents one possible modeled year of growth for a specifc historic time range. The larger dashed lines are the average account values for each account type. The blue dotted line is the tracking the after tax cash deposits made.
        """

spending_plot_title_md = "# <ins>FIRE (Financial Independence, Retire Early) Plot:</ins>"

spending_plot_info_md = """
        ### These plots shows total growths of all your accounts including retirement age and spending.

        #### There are two plots: the Liquid and Net Asset plots. They are the same but the Liquid Asset plot shows just liquid assets (i.e. You are only able to withdraw qualified medical expenses from an HSA without receiving a large fine.) Each faint line represents one possible modeled year of growth for a specifc historic time range. The larger dashed line is the average account value over time. 
        #### The additonal statistics help show the the number of sucessful models (any models that never had a 0 total account balance) as well as the 25% and 75% quantile ending balance.

        """