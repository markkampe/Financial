package simulation;

import java.util.NoSuchElementException;

/**
 * a tax computer based on mnimum + brackets/rates
 * (with built-in bracket-inflation and rate-creep)
 * 
 * @author Mark
 */
public class TaxRates {
	private String name;		// name of this tax
	private Bracket schedule[];	// schedule for this tax
	private int numBrackets;	// number of brackets in this schedule	
	
	// I could do something more dynamic, but why?
	private static final int MAX_BRACKETS = 10;	
	
	private int firstYear;		// base year for this schedule
	private Rate baseFunction;		// minimum tax inflation function
	private Rate bracketFunction;	// bracket inflation function
	private Rate rateFunction;		// rate inflation function
	private int minTax;			// minimum tax

	public boolean debug;		// debug output for this tax
	
	/**
	 * create a new set of tax rates
	 * 
	 * @param taxname		name of this tax	
	 * @param baseYear		base year for tables
	 * @param baseCreep		base tax inflation function
	 * @param bracketCreep	bracket creep function
	 * @param rateCreep		rate inflation function
	 */
	public TaxRates(String taxname, Rate baseCreep, Rate bracketCreep, Rate rateCreep ) {
		name = taxname;
		schedule = new Bracket[MAX_BRACKETS];
		numBrackets = 0;
		firstYear = 0;
		minTax = 0;
		bracketFunction = bracketCreep;
		rateFunction = rateCreep;
		debug = false;
	}
	
	/**
	 * add another rate bracket to a Tax Rate schedule
	 * 
	 * @param year			base year for this bracket
	 * @param newBracket	initial values for this bracket
	 */
	public void addBracket( int year, Bracket newBracket ) throws NoSuchElementException {
		if (numBrackets >= MAX_BRACKETS)
			throw new NoSuchElementException("Too many tax brackets");
		if (firstYear == 0)
			firstYear = year;
		else if (firstYear != year)
			throw new NoSuchElementException("Brackets w/different base years");
		
		schedule[numBrackets++] = newBracket;
	}
	
	/**
	 * set the minimum tax for the base year
	 * <P>
	 * NOTE: This parameter (which defaults to zero) is for use
	 * 		 in situations where the tax bill is some base amount
	 * 		 PLUS a graduated tax based on the total income/value.
	 * 		 (e.g. property insurance).
	 * 
	 * 		 It is scaled by its inflation function and used as
	 * 		 the initial value for the tax before we start using
	 * 		 the rate schedules.
	 * 
	 * @param amount	amount of minimum tax in base year
	 */
	public void setMinimumTax( int amount ) {
		minTax = amount;
	}
	
	/**
	 * compute the marginal tax rate
	 * 
	 * @param year	year of desired rate
	 * @param total	total amount of subject income
	 */
	public double getMarginalRate( int year, int total ) {
		double bracketInflation = 1.0;
		double rateInflation = 1.0;
		for( int yr = firstYear; yr < year; yr++ ) {
			if (bracketFunction != null) {
				bracketInflation *= 1 + bracketFunction.rateForYear(yr);
			}
			if (rateFunction != null) {
				rateInflation *= 1 + rateFunction.rateForYear(yr);	
			}
		}
		
		for(int i = 0; i < numBrackets; i++ ) {
			if (schedule[i].income == Bracket.UNLIMITED)
				return rateInflation * schedule[i].rate;
			
			double max = schedule[i].income * bracketInflation;
			if (max >= total)
				return rateInflation * schedule[i].rate;
		}
		throw new NoSuchElementException("no matching bracket found");
	}
	
	/**
	 * compute the tax on an amount using a schedule of tax
	 * brackets, inflation/creep adjusted to the desired year
	 * 
	 * @param year		year for which taxes are being computed
	 * @param amount	amount of income/value to be taxed
	 * 
	 * @return			computed tax amount
	 */
	public int taxOn( int year, int amount ) {
		// compute the bracket and rate creep
		double bracketInflation = 1.0;
		double rateInflation = 1.0;
		double baseInflation = 1.0;
		for( int yr = firstYear; yr < year; yr++ ) {
			if (baseFunction != null) {
				baseInflation *= 1 + baseFunction.rateForYear(yr);
			}
			if (bracketFunction != null) {
				bracketInflation *= 1 + bracketFunction.rateForYear(yr);
			}
			if (rateFunction != null) {
				rateInflation *= 1 + rateFunction.rateForYear(yr);	
			}
		}
		
		// are we debugging this tax
		if (debug) {
			String output = "tax=" + name + ", year=" + year + ", amt=" + amount;
			output += ", base=" + baseInflation + ", bf=" + bracketInflation + ", rf=" + rateInflation;
			System.out.println(output);
		}
		
		// see if there is a base tax (even for zero value)
		int taxSoFar = 0;
		if (minTax > 0) {
			double min = minTax * baseInflation;
			taxSoFar = (int) min;
		}
		
		// now run through the tables to compute the tax based
		// on a succession of marginal tax rates
		int taxedSoFar = 0;
		
		for( int i = 0; i < numBrackets && taxedSoFar < amount; i++ ) {
			// how much income is subject to this bracket
			int subject = amount;
			if (schedule[i].income != Bracket.UNLIMITED) { 
				double max = schedule[i].income * bracketInflation;
				if (max < subject)
					subject = (int) max;
			}
			
			// compute the tax on that amount
			double rate = schedule[i].rate * rateInflation;
			double tax = rate * (subject - taxedSoFar);
			taxSoFar += tax;
			
			// are we debugging this tax
			if (debug) {
				String output = "    subj=" + (subject-taxedSoFar);
				output += ", rate=" + rate + ", tax=" + tax ;
				System.out.println(output);
			}	
			
			// and move on to the next bracket
			taxedSoFar = subject;	
		}
		
		if (debug) {
			String output = "    total_tax=" + taxSoFar;
			System.out.println(output);
		}	
		return taxSoFar;
	}
}
