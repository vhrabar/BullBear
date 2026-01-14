export type EarningsReport = {
  id: string | number;
  fiscal_quarter: string | number;
  fiscal_year: string | number;
  report_date: string;
  estimate_eps?: string | number | null;
  actual_eps?: string | number | null;
};


export type Dividend = {
  id: string | number;
  ex_date: string;
  dividend_amount: number | string;
  currency: string;
  payment_date: string;
};
