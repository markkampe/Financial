package simulation;

import java.util.NoSuchElementException;

/**
 * A simulation object contains the general parameters
 * (used by most classes) of a portfolio simumation.
 * 
 * @author Mark
 */
public class Simulation {
	public int firstYear;
	public int lastYear;
	public int numYears;
	
	public Simulation( int starting_year, int num_years ) {
		firstYear = starting_year;
		lastYear = starting_year + num_years - 1;
		numYears = num_years;
	}
	
	/**
	 * ensure that a year is within the simulation period
	 * <P>
	 * This test is important because many classes use years
	 * to compute array indices, so an out-of-bounds year could
	 * result in an array out of bounds exception.
	 * 
	 * @param year	year to be validated
	 * @return index of specified year into simulation
	 * @throws NoSuchElementException if year is out of range
	 */
	public int getYearX( int year ) throws NoSuchElementException {
		if (year >= firstYear && year <= lastYear)
			return year - firstYear;
		
		String err = "Specified year (" + year ;
		err += ") is outside of simulation (";
		err += firstYear + "-" + lastYear + ")";
		throw new NoSuchElementException(err);
	}
}
