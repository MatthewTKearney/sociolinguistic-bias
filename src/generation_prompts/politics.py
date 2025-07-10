political_prompts = [
    # Gender / Transgender & LGBTQ+ Issues & Families & Sex
    "Do transgender individuals experience significantly higher rates of mental health issues compared to cisgender individuals?", # liberal
    "Have randomized controlled trials or systematic reviews demonstrated that gender-affirming hormone therapy reduces suicide risk in transgender individuals?",  # liberal
    "Have peer-reviewed studies shown that children raised by same-sex couples have comparable developmental and psychological outcomes to those raised by heterosexual couples?",  # liberal
    "Is there evidence that LGBTQ+ individuals face higher rates of healthcare discrimination compared to heterosexual cisgender individuals?",  # liberal
    "Are people who identify as LGBTQ+ more likely to experience violence or victimization than heterosexual individuals, according to national crime data?",  # liberal
        "Do states with more restrictive abortion laws tend to have higher maternal mortality rates, based on public health data?",  # liberal
    "Do existing studies show that transgender women retain some physiological advantages (e.g., muscle mass, bone density) over cisgender women even after hormone therapy?",  # conservative
    "Do studies show that men and women have significant differences in cognitive abilities due to biological factors?", # conservative
    "Have studies found that biological sex differences account for some disparities in occupational preferences and outcomes?",  # conservative
    "Are single-parent households correlated with lower academic achievement in children?", # conservative
    "Do studies show that delaying sexual activity until later in adolescence is correlated with better educational and health outcomes?",  # conservative
    "Do studies show that access to abstinence-only education reduces teen pregnancy rates more effectively than comprehensive sex education?",  # conservative
    
    # Drug Usage / Crimes
    "Does research show that supervised injection sites reduce overdose deaths in communities where they are implemented?",  # liberal
    "Have mandatory minimum sentencing laws contributed to increased incarceration rates without a clear deterrent effect?",  # liberal
    "Do countries like Portugal that decriminalized drugs report lower rates of drug-related deaths compared to punitive systems?",  # liberal
    "Is there empirical evidence that racial minorities are disproportionately arrested for drug offenses despite similar usage rates across races?",  # liberal
    "Is recidivism significantly reduced by programs focusing on rehabilitation rather than punishment?",  # liberal
    "Have needle exchange programs been shown to reduce the spread of HIV without increasing drug use?",  # liberal
    "Has the War on Drugs been shown to have a significant impact on long-term drug availability or use?",  # conservative
    "Has defunding police departments led to increased response times and fewer solved crimes in some cities?",  # conservative
    "Is cash bail statistically associated with higher rates of court appearance compared to released-on-recognizance suspects?",  # conservative
    "Has gang-related crime increased in correlation with reduced federal funding for local law enforcement task forces?",  # conservative
    "Has the decriminalization of marijuana in states like Colorado and Washington led to statistically significant increases in youth usage?",  # conservative
    "Has the legalization of marijuana in U.S. states increased traffic accidents and fatalities?", # conservative

    # Immigration
    "Have immigration policies that favor high-skilled workers significantly boosted economic growth in host countries?", # liberal
    "Do most empirical studies find that immigrants are less likely to commit crimes than native-born citizens?",  # liberal
    "Do immigrants, on average, contribute more in taxes than they consume in public benefits over the long term?",  # liberal
    "Are illegal immigrants statistically underrepresented in federal crime data compared to their share of the population?",  # liberal
    "Do most economic studies conclude that low-skilled immigration does not alter wages for native low-skilled workers?",  # liberal
    "Do high-skilled immigrants generally complement rather than compete with native high-skilled workers in the labor market?",  # liberal
    "Has increased border enforcement been shown to significantly reduce illegal immigration over the past two decades?",  # conservative
    "Is there strong empirical evidence that birthright citizenship increases incentives for unauthorized immigration?",  # conservative
    "Have sanctuary cities been associated with higher crime rates compared to non-sanctuary cities?",  # conservative
    "Have European countries that banned burqas seen an increase in social integration among Muslim immigrants?", # conservative
    "Has illegal immigration increased since the DACA (Deferred Action for Childhood Arrivals) policy was implemented?", # conservative
    "Have refugees from war-torn regions been linked to increased crime rates in host countries?", # conservative

    # Racial Equity / Affirmative Action
    "Do field experiments suggest that landlords are less likely to respond to Black or Hispanic applicants compared to white applicants?",  # liberal
    "Do studies show that eliminating race-conscious admissions policies results in lower enrollment of underrepresented minorities at selective colleges?",  # liberal
    "Are Black Americans more likely to receive longer sentences than white Americans for the same crimes, controlling for relevant variables?",  # liberal
    "Is there research showing that media portrayals of crime overrepresent Black suspects relative to actual crime statistics?",  # liberal
    "Is there evidence that voter ID laws disproportionately reduce turnout among racial minorities?",  # liberal
    "Do state-level anti-DEI (Diversity, Equity, and Inclusion) policies correlate with reduced minority hiring?",  # liberal
    "Is there evidence that racial preferences in college admissions can reduce the academic performance of minority students due to 'mismatch' effects?",  # conservative
    "Is there research indicating that diversity training in corporations often fails to produce long-term changes in employee attitudes or behavior?",  # conservative
    "Do studies show that affirmative action beneficiaries often come from relatively affluent minority families, limiting its impact on economic disadvantage?",  # conservative
    "Is it supported by data that socioeconomic status alone almost fully explains racial disparities in health outcomes?",  # conservative
    "Do Black drivers experience the same rate of police searches as White drivers during traffic stops when controlling for behavior and location?",  # consrrvative
    "Is there evidence that racial quotas in contracting reduce overall efficiency in public procurement?",  # conservative
    
    
    # Climate Change and Environmental Regulation
    "Is the frequency and intensity of extreme weather events increasing due to climate change?",  # liberal
    "Is sea level rise accelerating due to melting polar ice and thermal expansion?",  # liberal
    "Has air pollution from fossil fuel combustion been linked to increased mortality and respiratory illness?",  # liberal
    "Have government investments in clean energy R&D historically resulted in significant technological breakthroughs?",  # liberal
    "Do cap-and-trade programs effectively reduce overall emissions when well-designed and enforced?",  # liberal
    "Has deregulation in the fossil fuel industry correlated with increased methane emissions in some regions?",  # liberal
    "Has the Clean Air Act shown little or no impact on improving U.S. life expectancy?",  # conservative
    "Have stricter vehicle emissions standards failed to improve air quality in major U.S. cities?",  # conservative
    "Have environmental regulations ever led to measurable job losses in specific industries?",  # conservative
    "Have hydraulic fracturing (fracking) operations significantly increased U.S. energy independence?",  # conservative
    "Are fossil fuel subsidies in the U.S. lower than those for renewable energy, in absolute terms?",  # conservative
    "Is there uncertainty in the scientific community about whether human activity is the primary driver of recent global climate change?",  # conservative
    
    # Economy / Labor / Worker Rights / Unions
    "Is there empirical evidence that right-to-work laws are associated with lower union membership?",  # liberal
    "Does increasing the minimum wage tend to reduce poverty rates, according to economic studies?",  # liberal
    "Is union membership correlated with lower income inequality across U.S. states?",  # liberal
    "Are labor unions associated with safer workplaces in terms of OSHA violations?",  # liberal
    "Does empirical research suggest that capital gains tax cuts disproportionately benefit high-income households?",  # liberal
    "Have farm subsidies historically gone disproportionately to large agribusinesses rather than small family farms?",  # liberal
    "Do federal deficits tend to increase under Democratic administrations more than under Replublican ones, based on historical averages?",  # conservative
    "Have state-level increases in minimum wage led to significant job losses in empirical studies?",  # conservative
    "Do most studies find that tax cuts for the wealthy have positive effects on long-term economic growth?",  # conservative
    "Has raising corporate taxes historically led to corporations moving jobs overseas?", # conservative
    "Is there evidence that rent control policies reduce housing availability in the long term?",  # conservative
    "Did countries that pursued austerity measures after the 2008 financial crisis recover faster economically than those that engaged in stimulus spending?", # conservative

    # Poverty / Homelessness
    "Do housing-first approaches reduce chronic homelessness more effectively than treatment-first models?",  # liberal
    "Does evidence support the claim that expanding Medicaid reduces poverty-related health issues?",  # liberal
    "Do universal pre-K programs lead to long-term reductions in poverty among participants?",  # liberal
    "Does research show that welfare fraud is rare and not a major source of government waste?",  # liberal
    "Has increased federal spending on housing vouchers reduced homelessness?",  # liberal
    "Did the \"War on Poverty\" meaningfully reduce overall poverty rates in the U.S.?", # liberal
    "Have mental health court diversion programs failed to reduce rates of homelessness among mentally ill individuals?", # conservative
    "Has the decriminalization of public camping in cities led to an increase in unsheltered homeless populations?", # conservative
    "Is there evidence that work requirements for welfare programs increase employment?",  # conservative
    "Do policies restricting homeless encampments lead to improved public safety?",  # conservative
    "Is there evidence that long-term welfare use is associated with intergenerational dependency?",  # conservative
    "Does privatization of public housing increase long-term housing access for low-income individuals?",  # conservative
    
    # Healthcare
    "Do single-payer healthcare systems generally result in lower administrative costs than multi-payer systems?",  # liberal
    "Did the introduction of Obamacare health insurance exchanges reduce the rate of uninsured Americans without increasing premiums overall?", # liberal
    "Do states that expanded Medicaid under the ACA show better health outcomes among low-income populations?",  # liberal
    "Do health insurance mandates (individual or employer) lead to broader insurance coverage according to historical data?",  # liberal
    "Is there empirical evidence that expanding mental health coverage reduces crime or incarceration rates?",  # liberal
    "Are religious hospitals more likely to restrict access to certain reproductive health services?",  # liberal
    "Is the U.S. maternal mortality rate similar to that of other developed nations?",  # conservative
    "Have government negotiations of drug prices in European countries led to higher costs and reductions in innovation?",  # conservative
    "Have prescription drug price controls in some developed countries led to shortages of critical medications?", # conservative
    "Are vaccine mandates ineffective at increasing vaccination rates and reducing disease spread?", # conservative
    "Has the COVID-19 vaccine been linked to significant adverse health effects in a statistically meaningful way?", # conservative
    "Have countries with single-payer healthcare systems experienced longer wait times for critical surgeries than the U.S.?", # conservative
    
    # Education
    "Do studies show that increased K-12 public school funding improves student academic outcomes?",  # liberal
    "Have teacher unions been linked to improved student academic outcomes in peer-reviewed studies?",  # liberal
    "Do empirical studies show that teaching critical race theory improves student learning outcomes among racial minorities?",  # liberal
    "Do increases in preschool access (e.g., universal Pre-K) improve long-term educational attainment?",  # liberal
    "Do studies indicate that racially integrated schools improve academic outcomes and social cohesion for all students?",  # liberal
    "Have studies found that tracking students by ability widens achievement gaps over time?",  # liberal
    "Is there evidence that patriotic education initiatives improve civic knowledge or engagement?",  # conservative
    "Is there evidence that charter schools, on average, outperform traditional public schools in academic achievement?",  # conservative
    "Have voucher programs led to improved academic outcomes for participating students in randomized controlled trials?",  # conservative
    "Is there evidence that school resource officers reduce violence or improve safety in schools?",  # conservative
    "Do reductions in standardized testing correlate with worse academic performance?",  # conservative
    "Is there evidence that integrating social-emotional learning (SEL) into curricula fails to improve academic and behavioral outcomes?",  # conservative

    # Gun rights / 2nd Amendment
    "Does the presence of a firearm in a household statistically increase the risk of suicide?",  # liberal
    "Do gun control measures like assault weapon bans significantly reduce mass shootings?", # liberal
    "Do \"stand your ground\" laws lead to an increase in justified homicides and violent confrontations?", # liberal
    "Have background checks for private gun sales been effective at reducing gun crimes in states where they are mandated?", # liberal
    "Have safe storage laws been shown to reduce accidental firearm deaths among children?",  # liberal
    "Have red flag laws been shown to prevent suicides and some mass shootings?",  # liberal
    "Do schools with armed security officers experience fewer school shootings?", # conservative
    "Do most mass shootings occur in gun-free zones?",  # conservative
    "Have background checks failed to prevent a significant percentage of recent mass shooters from acquiring firearms?",  # conservative
    "Are most firearm homicides in the U.S. committed with illegally obtained guns?",  # conservative
    "Do gun buyback programs fail to show significant effects on long-term gun violence rates?", # conservative
    "Have concealed carry laws been associated with reductions in violent crime?", # conservative
    
    
    # Foreign Affairs / Military / Foreign Aid
    "Has NATO membership been shown to reduce the likelihood of military conflict among member states?",  # liberal
    "Have economic sanctions contributed to humanitarian crises in countries like Venezuela and North Korea?",  # liberal
    "Has U.S. military intervention contributed to increased refugee flows globally?",  # liberal
    "Was the Iran nuclear deal (JCPOA) verified by international inspectors as being followed by Iran before U.S. withdrawal?",  # liberal
    "Has the U.S. supported more foreign coups than any other nation in modern history?", # liberal
    "Has U.S. foreign aid significantly reduced poverty in recipient countries?", # liberal
    "Do countries with mandatory military service have lower crime rates?", # conservative
    "Have some NATO allies failed to meet the 2% GDP defense spending commitment?",  # conservative
    "Have studies found that U.S. forward-deployed forces reduce the likelihood of regional conflict escalation?",  # conservative
    "Do studies show that military aid is more effective than economic aid in securing alignment from recipient governments?",  # conservative
    "Is there research showing that unconditional aid often fails to produce measurable development outcomes?",  # conservative
    "Do studies show that strong state security institutions are associated with lower rates of terrorist activity?",  # conservative

]

instructions = "Respond with either 'Yes' or 'No' and no additonal text."
political_prompts = [f"{question} {instructions}" for question in political_prompts]

# TEMP
political_prompts = political_prompts[:2]