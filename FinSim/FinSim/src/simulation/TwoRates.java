package simulation;

/**
 * two-line growth rate - a rate that takes on two values over
 * the course of the simulation (e.g rising, then flat)
 * 
 * @author markk
 */
public class TwoRates extends Rate {

		private double rate1, rate2;
		private int year2;
		

		/**
		 * create a three-line rate function
		 * 
		 * @param rate_1	initial rate
		 * @param year_2	year in which we change to second rate
		 * @param rate_2	second rate
		 */
		TwoRates(	double rate_1,
						int year_2, double rate_2) {
			
			rate1 = rate_1;
			rate2 = rate_2;
			year2 = year_2;
		}
		
		public double rateForYear(int year) {
			if (year < year2)
				return rate1;
			return rate2;
		}
}
