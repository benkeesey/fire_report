CREATE SCHEMA `firedb` ;

ALTER TABLE `firedb`.`yearly_market_df` 
CHANGE COLUMN `Year` `Year` BIGINT NOT NULL ,
CHANGE COLUMN `Real_Return_Percentage` `Real_Return_Percentage` DOUBLE NOT NULL ,
ADD PRIMARY KEY (`Year`),
ADD UNIQUE INDEX `Year_UNIQUE` (`Year` ASC) VISIBLE;
;


CREATE TABLE `firedb`.`user_fire_report_info` (
  `user_id` VARCHAR(45) NOT NULL,
  `name` VARCHAR(45) NULL,
  `age` INT NULL,
  `retirement_age` INT NULL,
  `yearly_savings` INT NULL,
  `time_window` INT NULL,
  `retirement_spend` INT NULL,
  `yearly_HSA_qualified_expense` INT NULL,
  `balance_HSA` INT NULL,
  `balance_brokerage` INT NULL,
  `balance_401k` INT NULL,
  `balance_roth` INT NULL,
  `balance_HSA_qualified_expense` INT NULL,
  `balance_401k_contributions` INT NULL,
  `growth_comparison_starting_balance` INT NULL,
  `HSA_contribution_limit` INT NULL,
  `Roth_contribution_limit` INT NULL,
  `Traditional_401k_contribution_limit` INT NULL,
  `Expense_Ratio` REAL NULL,
  `Marginal_Tax_Rate` INT NULL,
  `Capital_Gains_Tax` INT NULL,
  `Retired_Marginal_Tax_Rate` INT NULL,
  `Retired_Capital_Gains_Tax` INT NULL,
  `color_scheme` VARCHAR(45) NULL,
  PRIMARY KEY (`user_id`))
COMMENT = 'Contains all parameters used to run fire report';