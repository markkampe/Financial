package simulation;

/**
 * three-line growth rate - a rate that takes on three values over
 * the course of the simulation (e.g rising, flat, falling)
 * 
 * @author markk
 */
public class ThreeRates extends Rate {

		private double rate1, rate2, rate3;
		private int year2, year3;
		

		/**
		 * create a three-line rate function
		 * 
		 * @param rate_1	initial rate
		 * @param year_2	year in which we change to second rate
		 * @param rate_2	second rate
		 * @param year_3	year in which we change to final rate
		 * @param rate_3	final rate
		 */
		ThreeRates(	double rate_1,
						int year_2, double rate_2,
						int year_3, double rate_3) {
			
			rate1 = rate_1;
			rate2 = rate_2;
			rate3 = rate_3;
			year2 = year_2;
			year3 = year_3;
		}
		
		public double rateForYear(int year) {
			if (year < year2)
				return rate1;
			if (year < year3)
				return rate2;
			return rate3;
		}
}
