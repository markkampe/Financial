package simulation;

import java.util.NoSuchElementException;

/**
 * general purpose income tax computation engine
 * driven by rate schedules and pre/post tax deduction formulae.
 * <P>
 * It is intended that this engine be general enough to be
 * usable to reasonably approximate any income tax.
 *
 * @author Mark
 */
public class IncomeTax {

	private Simulation sim;		// global simulation parameters
	private TaxRates schedule;	// applicable schedule
	private TaxRates divRates;	// dividend rate schedule
	private TaxRates ltgRates;	// long term gains rate schedule
	private int preTaxDed;		// amount to subtract from pre-tax income
	private int postTaxDed;		// amount to subtract from tax
	private int freeInterest;	// non-taxable interest
	private int standardDed;	// standard deduction amount
	private int maxDedLoss;		// maximum annually deductible loss
	private Rate inflation;		// inflation factor for deductions
								// but NOT freeInterest nd maxDedLoss
	private int loss[];			// losses carried forward
	
	public boolean debug;
	
	/**
	 * create a new income tax engine
	 * <P>
	 * Note that the dividend rate and CG rate schedules are
	 * 	    not used to compute tax (based on amount of dividend)
	 * 	    but to find the marginal rate (based on taxable income).
	 * 
	 * @param taxSchedule		basic rate schedule
	 * @param dividendRates		rate schedule for qualifying dividends
	 * @param CGRates			rate schedule for long-term gains
	 * @param standardDeduction	standard deduction
	 * @param inflationRate		inflation function for parametrized amounts
	 * @param baseYear			base year for above amounts
	 * @param sim.numYears			number of years in simulation
	 */
	public IncomeTax( TaxRates taxSchedule,
					  TaxRates dividendRates,
					  TaxRates CGRates,
					  int standardDeduction,
					  Rate inflationRate,
					  Simulation simParms ) {
		schedule = taxSchedule;
		divRates = dividendRates;
		ltgRates = CGRates;
		
		loss = new int[sim.numYears+1];
		for( int i = 0; i <= sim.numYears; i++ ) 
			loss[i] = 0;
		
		standardDed = standardDeduction;
		inflation = inflationRate;
		
		sim = simParms;
	
		preTaxDed = 0;
		postTaxDed = 0;
		freeInterest = 0;
		maxDedLoss = 0;
		debug = false;
	}
	
	/**
	 * set the value of a loss carried in
	 * <P>
	 * NOTE: unlike everything else, the array of losses begins
	 * 		 the year before the simulation does.  This is because
	 * 		 that loss can be carried forward into the first year
	 * 		 of the simulation.
	 * 
	 * @param	year in which loss was incurred
	 * @param 	amount of loss carried in to first year
	 */
	public void setLoss( int year, int value ) {
		if (year != sim.firstYear - 1)
			sim.getYearX(year);
	
		loss[year - (sim.firstYear-1)] = value;
	}
	
	/**
	 * return the loss carried forward from the specified year
	 * 
	 * @param year	desired year
	 * @return		loss carried forward from that year
	 */
	private int getLoss( int year ) throws NoSuchElementException {
		if (year != sim.firstYear - 1)
			sim.getYearX(year);
		return loss[year - (sim.firstYear-1)];
	}
	
	/**
	 * set (TAX PARAMETER) amount of interest that is tax-free
	 * 
	 * @param value	amount of tax-free interest allowed
	 */
	public void setFreeInterest( int value ) {
		freeInterest = value;
	}
	
	/**
	 * set (TAX PARAMETER)standard amount to be deducted from income,
	 * in addtion to standard deductions and before consulting
	 * the tax schedule
	 * 
	 * @param value	amount to subtract
	 */
	public void setPreTaxDeduction( int value ) {
		preTaxDed = value;
	}
	
	/**
	 * set (TAX PARAMETER) standard amount to be subtracted from the 
	 * looked up tax (e.g. california personal exemptions)
	 * (independently of any other credits)
	 * 
	 * @param value	amount to be subtracted
	 */
	public void setPostTaxCredit( int value ) {
		postTaxDed = value;
	}
	
	/**
	 * set )TAX PARAMETER) maximum allowable deduction of long term
	 * losses from each year's income.
	 * 
	 * @param value	maximum allowable annual income offset for long term losses
	 */
	public void setMaxDeductibleLoss( int value ) {
		maxDedLoss = value;
	}
	
	/**
	 * compute the income tax associated with an income collection
	 * <P>
	 * This is the general tax engine, controlled by rate tables
	 * and parameters specified when it was created.  The general
	 * formula is pretty simple:
	 * 	(1) subtract built-in pre-tax deductions
	 *  (2) subtract specified deductions for this year
	 *      (or built-in standard deduction)
	 *  (3) compute the tax using the specified tax rates
	 *  (4) subtract built-in post-tax credits
	 *  (5) subtract specified credits for this year
	 * <P>
	 * This basic formula is only slightly complicated by
	 *  (1) there may be an allowed amount of free interest
	 *  (2) there may be some capital loss carry forward
	 *  (3) there may be preferential taxation of qualified dividends
	 *  (4) there may be preferential taxation of long term gains
	 * 
	 * @param year		year for which tax should be computed
	 * @param income	all income that is not eligible for preferential treatment 
	 * @param interest	interest that may receive preferential treatment
	 * @param qDividends dividends that may receive preferential treatment
	 * @param ltGains	long term gains that may receive preferential treatment
	 * @param deductions itemized deductions
	 * 					NOTE: these are in addition to the pre-tax
	 * 						  deductions included in the tax parameters.
	 * @param credits	tax credits (beyond personal exemptions)
	 * 					NOTE: these are in addition to the post-tax
	 * 				 		  credits in the tax parameters.
	 * 
	 * @return		the estimated tax for that year
	 */
	public int taxOn( int year,
					  int income,  int interest, int qDividends, int ltGains,
					  int deductions,
					  int credits ) {
		
		// figure out how much to inflate our factors
		double inflate = (inflation == null) ? 1.0 :
										inflation.compounded(sim.firstYear, year);
		
		// if no preferential divident treatment, roll them into income
		int addDiv = 0;
		if (divRates == null) {
			addDiv = qDividends;
			qDividends = 0;
		}
		
		// figure out how to handle long-term capital gains
		int addLtg = 0;
		ltGains -= getLoss(year - 1);
		if (ltGains >= 0) {	// net gain
			setLoss(year, 0);
			if (ltgRates == null) {	// treat them as income
				addLtg = ltGains;
				ltGains = 0;
			}
		} else {			// net loss
			int netloss = -ltGains;
			if (netloss < maxDedLoss) {
				addLtg = ltGains;
				setLoss( year, 0 );
			} else {
				addLtg = -maxDedLoss;
				setLoss( year, netloss - maxDedLoss );
			} 
			ltGains = 0;
		}
		
		// a small amount of interest may be tax exempt
		int addInt = 0;
		if (interest > freeInterest) {
				addInt = interest - freeInterest;
		}
		
		// anything that won't receive preferential treatment
		// gets rolled in to the adjusted gross income
		int agi = income + addDiv + addLtg + addInt;
		
		if (debug) {
			System.out.println("income=" + income +
					" +int=" + addInt +
					" +div=" + addDiv +
					" +ltg=" + addLtg );
		}
		
		// inflation-adjusted built-in pre-tax deductions
		double preTaxSub = preTaxDed * inflate;
		
		// see if (inflation adjusted) standard deduction beats supplied
		double ded = standardDed * inflate;
		if (deductions > ded)
			ded = deductions;
		
		// compute the taxable income
		int taxable = (int) (agi - (preTaxSub + ded));
		if (taxable < 0)
			taxable = 0;
		
		if (debug) {
			System.out.println("agi=" + agi + ", DED=" + preTaxSub +
					", ded=" + ded + ", taxable=" + taxable );
		}
	
		// use the tax table to compute the basic tax
		int tax = schedule.taxOn(year, taxable);
		
		// qualified dividends may b taxed ay a special rate
		double dTax = 0;
		if (qDividends > 0) {
			dTax = qDividends * divRates.getMarginalRate(year, taxable);
		}
		
		// long term gains may be taxed at special rate
		ltGains = 0;
		double cgTax = 0;
		if (ltGains > 0) {
			cgTax = ltGains * ltgRates.getMarginalRate(year, taxable);
		}
		
		// apply (inflation adjusted) built-in post-tax credits
		int cred = (int)(postTaxDed * inflate);
		
		if (debug) {
			System.out.println("base tax=" + tax +
					", div=" + dTax + ", ltg=" + cgTax +
					", CRED=" + cred + ", cred=" + credits );
		}
		
		// TODO add support for AMT
		return (int) (tax + dTax + cgTax - (cred + credits));
	}
}
