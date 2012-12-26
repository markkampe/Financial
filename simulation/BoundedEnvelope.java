package simulation;

import java.util.NoSuchElementException;

/**
 * envelope that is (by default) 1.0 between specified years, 
 * and zero at all other times.
 * <P>
 * The most obvious use is for functions that only exist during
 * selected years (e.g. normal salary that ends at retirement, 
 * social security income beginning after 65, switching between
 * medical expense formulae when medicare kicks in). 
 * But it can also be used (with explicitly set values) for
 * functions that scale with external factors (e.g. groceries
 * or power consumption that scale with the number of people
 * living in the house.
 * 
 * @author markk
 *
 */
public class BoundedEnvelope implements Envelope
{
	private int firstYear;	
	private int lastYear;
	private double values[];
	private int numValues;
	
	/**
	 * create an envelope function that returns (by default) 
	 * 1.0 for the specified range and 0.0 for all other years
	 * <P>
	 * NOTE: the time duration of this function is not constrained
	 *       to be the same as the time duration of the simulation.
	 * 
	 * @param startYear	first year during which envelope is non-zero
	 * @param endYear	last year during which envelope is non-zero
	 */
	BoundedEnvelope( int startYear, int endYear ) {
		firstYear = startYear;
		lastYear = endYear;
		
		numValues = 1 + lastYear - firstYear;
	}
	
	/**
	 * set a value (other than the default 1.0) for a particular year
	 * 
	 * @param year	year for which value is to be set
	 * @param value	value for that year
	 * 
	 * @throws NoSuchElementException	if specified year is outside range
	 */
	public void setScaleForYear(int year, double value ) throws NoSuchElementException {
		if (year < firstYear || year > lastYear) {
			String err = "Attempt to set scale (year=" + year ;
			err += ") in BoundedEnvelope (";
			err += firstYear + "-" + lastYear + ")";
			throw new NoSuchElementException(err);
		}
		
		// if we don't already have a discrete values array, allocate it
		if (values == null) {
			values = new double[numValues];
			for( int i = 0; i < numValues; i++ )
				values[i] = 1.0;
		}
		values[ year - firstYear ] = value;	
	}
	
	/**
	 * return scaling factor for a specified year
	 * 
	 * @param	year for which scaling factor is desired
	 * 
	 * @return	scaling factor for that year
	 */
	public double scaleForYear(int year) {
		if (year < firstYear || year > lastYear)
			return( 0.0 );
		if (values == null)
			return 1.0;
		return values[year - firstYear];
	}
}
