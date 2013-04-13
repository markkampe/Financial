package simulation;

public class Test {
	
	public static void main( String args[] ) {
		int firstYear = 2011;
		int numYears = 40;
		
		Simulation sim = new Simulation( firstYear, numYears );
		
		// testExpense(sim);
		testIncome(sim);
		// testTaxes(sim);
		// testInvest(sim);
		// testProperty(sim);
	}

	private static void testExpense( Simulation sim ) {
		Expenses ndisc = new Expenses( "SUMMARY", "nondiscretionary", sim );
		
		BoundedEnvelope residents = new BoundedEnvelope( sim.firstYear, sim.lastYear );
		residents.setScaleForYear(2013, 0.9);
		
		Expense groc = new Expense( "groc", "nondiscretionary",
				residents, new TwoRates( .04, 2028, 0), 
				null, sim );
		groc.setExpense( sim.firstYear, 11400 );
		ndisc.addExpense( groc, false );
		
		Expense hh = new Expense( "hhold", "nondiscretionary",
				null,  new SingleRate( .05 ),
				null, sim );
		hh.setExpense( sim.firstYear, 4200 );
		ndisc.addExpense( hh, false );
		
		Expense am = new Expense( "amort", "nondiscretionary",
				null,  new SingleRate( .04 ),
				null, sim );
		am.setExpense( sim.firstYear, 3600 );
		ndisc.addExpense( am, false );
		
		Expense transp = new Expense( "transp", "nondiscretionary",
				null,  new TwoRates( .05, 2028, 0),
				null, sim );
		transp.setExpense( sim.firstYear, 6600 );
		ndisc.addExpense( transp, false );
		
		Expense util = new Expense( "util", "nondiscretionary",
				residents,  new SingleRate( .05 ),
				null, sim );
		util.setExpense( sim.firstYear, 7740 );
		ndisc.addExpense(util, false);
		
		// TODO MD estimate is poorly based, but plausible
		Expense md = new Expense( "health", "nondiscretionary",
				new BoundedEnvelope( 2010, 2017 ),  new SingleRate( .06 ),
				null, sim );
		md.setExpense( sim.firstYear, 13200 );
		ndisc.addExpense(md, false);
		
		// TODO medicare estimate is poorly based but plausible
		Expense mcare = new Expense( "medicare", "nondiscretionary",
				new BoundedEnvelope( 2018, 2100 ),  new SingleRate( .055 ),
				null, sim );
		mcare.setExpense( 2017, 16336);
		ndisc.addExpense(mcare, false);
		
		Expense ed = new Expense( "edu", "nondiscretionary", 
				new BoundedEnvelope(sim.firstYear, 2015), null,
				null, sim );
		ed.setExpense( sim.firstYear, 1200 );
		ndisc.addExpense(ed, false);
		
		Expenses disc = new Expenses( "SUMMARY", "discretionary", sim );
		
		Expense cl = new Expense( "clothes", "discretionary",
				residents,  new TwoRates( .05, 2023, 0),
				null, sim );
		cl.setExpense( sim.firstYear, 2400 );
		disc.addExpense(cl, true);
		
		Expense don = new Expense( "charity", "discretionary",
				null,  new SingleRate( .07 ),
				null, sim );
		don.setExpense( sim.firstYear, 1800 );
		disc.addExpense( don, true );
		
		Expense ff = new Expense( "food/fun", "discretionary",
				residents,  new TwoRates( .05, 2028, 0),
				null, sim );
		ff.setExpense( sim.firstYear, 7200 );
		disc.addExpense(ff, true);
		
		Expense gi = new Expense( "gifts", "discretionary",
				null,  new SingleRate( .07 ),
				null, sim );
		gi.setExpense( sim.firstYear, 2100 );
		disc.addExpense(gi, true);
		
		Expense ho = new Expense( "hobbies", "discretionary",
				null,  new TwoRates( .05, 2023, 0),
				null, sim );
		ho.setExpense( sim.firstYear, 1200 );
		disc.addExpense(ho, true);
		
		Expense misc = new Expense( "misc", "discretionary",
				residents,  new SingleRate( .05 ),
				null, sim );
		misc.setExpense( sim.firstYear, 1200 );
		disc.addExpense(misc, true);
		
		Expense toy = new Expense( "toys", "discretionary",
				residents, new TwoRates( .05, 2023, 0), 
				null, sim );
		toy.setExpense( sim.firstYear, 1800 );
		disc.addExpense(toy, true);
		
		Expense vac = new Expense( "vac", "discretionary",
				null,  new TwoRates( .10, 2024, 0), 
				null, sim );
		vac.setExpense( sim.firstYear, 15000 );
		disc.addExpense(vac, true);
		
		for( int y = sim.firstYear; y <= sim.lastYear; y++ ) {
			for( int i = 0; i < ndisc.numExpenses; i++ ) {
				String summary = ndisc.expenses[i].toString(y);
				if (summary != null)
					System.out.println(summary);
			}
			
			for( int i = 0; i < disc.numExpenses; i++ ) {
				String summary = disc.expenses[i].toString(y);
				if (summary != null)
					System.out.println(summary);
			}
			
			System.out.println(ndisc.toString(y));
			System.out.println(disc.toString(y));
			System.out.println();
		}
	}
	
	private static void testIncome(Simulation sim) {
		
		Incomes mkWages = new Incomes("SUMMARY", "mark", sim );
		Incomes lkWages = new Incomes("SUMMARY", "lynnette", sim );
		
		Income hds = new Income(
				"HDS",
				"mark", 
				new BoundedEnvelope( 2011, 2012), 
				new SingleRate( 0.03),
				19500, sim );
		hds.setIncome( 2011, 199200 );
		hds.setIncome(2012, 208000 );
		mkWages.addSource(hds);
		
		Income tpf = new Income(
				"TPF",
				"lynnette", 
				new BoundedEnvelope( 2011, 2012), 
				new SingleRate( 0.015),
				0, sim );
		tpf.setIncome( 2011, 45000 );
		lkWages.addSource(tpf);
		
		Income ucla = new Income(
				"UCLA",
				"mark", 
				new BoundedEnvelope( 2011, 2011), 
				new SingleRate( 0.02),
				300, sim );
		ucla.setIncome( 2011, 3991 );
		mkWages.addSource(ucla);
		
		Income cmc = new Income(
				"CMC",
				"mark", 
				new BoundedEnvelope( 2011, 2011), 
				new SingleRate( 0.02),
				0, sim );
		cmc.setIncome( 2011, 3000 );
		mkWages.addSource(cmc);
		
		Income scuba = new Income(
				"SCUBA",
				"mark", 
				new BoundedEnvelope( 2011, 2012), 
				new SingleRate( 0.00),
				0, sim );
		scuba.setIncome( 2011, 500 );
		mkWages.addSource(scuba);
		
		Income ssi = new Income(
				"SSI",
				"mark", 
				new BoundedEnvelope( 2015, 2052),
				new SingleRate( 0.02),
				0, sim );
		ssi.setIncome( 2015, 1763*12 );
		mkWages.addSource(ssi);
		
		Income ssi2 = new Income(
				"SSI",
				"lynnette", 
				new BoundedEnvelope( 2015, 2052),
				new SingleRate( 0.02),
				0, sim );
		ssi2.setIncome( 2015, 867*12 );
		lkWages.addSource(ssi2);
	
		
		// print out a line for each year
		for( int y = sim.firstYear; y <= sim.lastYear; y++ ) {
			for( int i = 0; i < mkWages.numSources; i++ ) {
				String summary = mkWages.sources[i].toString(y);
				if (summary != null)
					System.out.println(summary);
			}
			for( int i = 0; i < lkWages.numSources; i++ ) {
				String summary = lkWages.sources[i].toString(y);
				if (summary != null)
					System.out.println(summary);
			}
			System.out.println( mkWages.toString(y));
			System.out.println( lkWages.toString(y));
			
			System.out.println();
		}
		
		// TODO model taxes on income
	}
	
	private static void testInvest(Simulation sim) {
		
		Assets portfolio = new Assets("Portfolio", sim);
		
		Asset cash = new Asset(
				"cash",
				null,
				new SingleRate(0.025),
				null,
				null,
				true,
				sim );
		portfolio.addAsset(cash);
		cash.setValue( sim.firstYear, 494454, 494454 );
		
		Asset taxEq = new Asset(
				"tax eqty",
				new SingleRate(0.01),
				null,
				new SingleRate(0.01),
				new SingleRate(0.06),
				true,
				sim );
		portfolio.addAsset(taxEq);
		taxEq.setValue( sim.firstYear, 821676, 528193 );
		
		Asset taxDbt = new Asset(
				"tax debt",
				new SingleRate(0.01),
				new SingleRate(0.02),
				new SingleRate(0.01),
				null,
				true,
				sim );
		portfolio.addAsset(taxDbt);
		taxDbt.setValue( sim.firstYear, 0, 0 );
		
		Assets zeroes = new Assets("zero ladder", sim );
		portfolio.addAsset(zeroes);
		zeroes.addAsset( new Bond("2011", 45000, 25596, null, sim.firstYear, 2011, sim ));
		zeroes.addAsset( new Bond("2012", 45000, 24316, null, sim.firstYear, 2012, sim ));
		zeroes.addAsset( new Bond("2013", 50000, 25667, null, sim.firstYear, 2013, sim ));
		zeroes.addAsset( new Bond("2014", 20000,  9753, null, sim.firstYear, 2014, sim ));
		zeroes.addAsset( new Bond("2015", 55000, 25481, null, sim.firstYear, 2015, sim ));
		zeroes.addAsset( new Bond("2016", 45000, 19806, null, sim.firstYear, 2016, sim ));
		zeroes.addAsset( new Bond("2017", 50000, 20906, null, sim.firstYear, 2017, sim ));
		zeroes.addAsset( new Bond("2018", 55000, 21847, null, sim.firstYear, 2018, sim ));
		zeroes.addAsset( new Bond("2019", 60000, 22641, null, sim.firstYear, 2019, sim ));
		zeroes.addAsset( new Bond("2020", 60000, 21509, null, sim.firstYear, 2020, sim ));
		zeroes.addAsset( new Bond("2021", 65000, 22137, null, sim.firstYear, 2021, sim ));
		zeroes.addAsset( new Bond("2022", 35000, 11324, null, sim.firstYear, 2022, sim ));
		
		
		
		
		Asset mkIRA = new Asset(
				"IRA",
				new SingleRate(0.01),
				null,
				new SingleRate(0.01),
				new SingleRate(0.06),
				true,
				sim );
		portfolio.addAsset(mkIRA);
		mkIRA.setValue( sim.firstYear, 34309, 0 );
		
		Asset mkRoth = new Asset(
				"MK Roth",
				new SingleRate(0.01),
				null,
				new SingleRate(0.01),
				new SingleRate(0.06),
				true,
				sim );
		portfolio.addAsset(mkRoth);
		mkRoth.setValue( sim.firstYear, 350000, 350000 );
		
		Asset lkRoth = new Asset(
				"LK Roth",
				new SingleRate(0.01),
				null,
				new SingleRate(0.01),
				new SingleRate(0.06),
				true,
				sim );
		portfolio.addAsset(lkRoth);
		lkRoth.setValue( sim.firstYear, 58077, 58077 );

		for( int y = sim.firstYear; y <= sim.lastYear; y++ ) {
			for( int i = 0; i < portfolio.numAssets; i++) {
				String summary = portfolio.assets[i].toString(y);
				if (summary != null)
					System.out.println(summary);
			}
			System.out.println(portfolio.toString(y));
			System.out.println();
		}
		
		// TODO model taxes on assets

	}
	
	private static void testProperty( Simulation sim ) {
		TaxRates insSched = new TaxRates("Home ins", null, null, null );
		insSched.addBracket(sim.firstYear, new Bracket(Bracket.UNLIMITED, .00175));
		//insSched.debug = true;
		
		TaxRates propSched = new TaxRates("Prop Tax", null, null, null );
		//propSched.debug = true;
		propSched.addBracket(sim.firstYear, new Bracket(Bracket.UNLIMITED, .01));
		
		Property home = new Property( "Home", "RealEstate", 
				new SingleRate( 0.0225), new SingleRate( 0.01 ), 
				insSched, propSched, sim );
		home.setValue(2011, 898029, 416100, 372429);
		//home.debug = true;
		
		Property cabin = new Property( "Cabin", "RealEstate", 
				new SingleRate( 0.015), new SingleRate( 0.01 ), 
				insSched, propSched, sim);
		cabin.setValue(2011, 100126, 138100, 65000);
		cabin.improve(2013,500000, 500000/2, 500000);
		//cabin.debug = true;
		
		Properties props = new Properties("SUMMARY", "RealEstate", sim );
		props.addProperty(home);
		props.addProperty(cabin);
		
		// print out a value for each year
		for( int y = sim.firstYear; y <= sim.lastYear; y++ ) {
			for( int i = 0; i < props.numProperties; i++ ) {
				System.out.println( props.property[i].toString(y));
			}
			System.out.println(props.toString(y));
		}

		// TODO validate property tax formula against history
	}
	
	private static void testTaxes( Simulation sim ) {
		
		int mkTaxable = 206691;
		int mkRet = 19500+319;
		int lkTaxable = 45000;
		int interest = 9271;
		int div=12325-8135;
		int qdiv = 8135;
		int cg = 12941;
		int taxable = mkTaxable+lkTaxable+div;
		
		// TAX tables
		TaxRates fed = new TaxRates("FIT", null, null, new SingleRate(0.03));
		fed.addBracket( sim.firstYear, new Bracket(  17252, 0.10));
		fed.addBracket( sim.firstYear, new Bracket(  70039, 0.15));
		fed.addBracket( sim.firstYear, new Bracket( 141418, 0.28));
		fed.addBracket( sim.firstYear, new Bracket( 215527, 0.31));
		fed.addBracket( sim.firstYear, new Bracket( 384859, 0.36));
		fed.addBracket( sim.firstYear, new Bracket( Bracket.UNLIMITED, 0.40));
		
		TaxRates divRates = new TaxRates("QDiv", null, null, null );
		divRates.addBracket( sim.firstYear, new Bracket( 141418, 0.05));
		divRates.addBracket( sim.firstYear, new Bracket( Bracket.UNLIMITED, 0.15));
		
		TaxRates cgRates = new TaxRates("CG", null, null, null );
		cgRates.addBracket( sim.firstYear, new Bracket( Bracket.UNLIMITED, 0.20));
		
		IncomeTax fit = new IncomeTax(fed, divRates, cgRates, 
						11742, new SingleRate(0.03), 
						sim );
		fit.setPreTaxDeduction(15038);
		fit.setFreeInterest(200);
		fit.setMaxDeductibleLoss(3000);
		fit.setLoss(sim.firstYear-1, 95774);
		System.out.println(String.format("   fit=$%6d", 
							fit.taxOn(2011, taxable, interest, qdiv, cg, 0, 0 )));
		
		TaxRates cal = new TaxRates("SIT", null, null, new SingleRate(0.03));
		cal.addBracket( sim.firstYear, new Bracket(  14979, 0.0124));
		cal.addBracket( sim.firstYear, new Bracket(  35516, 0.0224));
		cal.addBracket( sim.firstYear, new Bracket(  56055, 0.0425));
		cal.addBracket( sim.firstYear, new Bracket(  77816, 0.0625));
		cal.addBracket( sim.firstYear, new Bracket(  98630, 0.0825));
		cal.addBracket( sim.firstYear, new Bracket( Bracket.UNLIMITED, 0.0955));
		IncomeTax sit = new IncomeTax(cal, null, null, 
				7274, new SingleRate(0.03), 
				sim);
		sit.setPostTaxCredit(196);
		sit.setMaxDeductibleLoss(3000);
		sit.setLoss(sim.firstYear-1, 95774);
		System.out.println(String.format("   sit=$%6d", 
						sit.taxOn(2011, taxable, interest, qdiv, cg, 0, 0 )));
		
		TaxRates fica = new TaxRates("FICA", null, null, new SingleRate(0.02));
		fica.addBracket( sim.firstYear, new Bracket( 110538, 0.0620));
		fica.addBracket( sim.firstYear, new Bracket( Bracket.UNLIMITED, 0.0));
		System.out.println(String.format(" mkssi=$%6d", fica.taxOn(2011, mkTaxable )));
		System.out.println(String.format(" lkssi=$%6d", fica.taxOn(2011, lkTaxable )));
		
		TaxRates med = new TaxRates("Medicare", null, null, new SingleRate(0.03));
		med.addBracket( sim.firstYear, new Bracket( Bracket.UNLIMITED, 0.0145));
		System.out.println(String.format(" mcare=$%6d", med.taxOn(2011, mkTaxable+mkRet+lkTaxable )));
		
		TaxRates sdi = new TaxRates("SDI", null, null, new SingleRate(0.03)); 
		sdi.addBracket( sim.firstYear, new Bracket(  93316, 0.011));
		sdi.addBracket( sim.firstYear, new Bracket( Bracket.UNLIMITED, 0));
		System.out.println(String.format(" mksdi=$%6d", sdi.taxOn(2011, mkTaxable )));
		System.out.println(String.format(" lksdi=$%6d", sdi.taxOn(2011, lkTaxable )));
	}
}
