from sentence_tokenization import SentenceBoundaryDetection


def test():
    sent_tokenizer = SentenceBoundaryDetection()
    sent_tokenizer.set_deid_pattern("\[\*\*|\*\*\]")

    text = '''
        Test: 
        1.  Lymphoplasmacytoid lymphoma involving bone marrow and spleen diagnosed  
        initially in [** Date **], associated with progressively increasing IgG kappa  
        paraprotein.  
        2.  Compression fractures of the spine secondary to lymphoma.  In the past,  
        it has been associated with significant back pain.  He is status post three  
        kyphoplasties.
        Test Again:
        should be in the same line 
    '''
    text1 = "INDUCTION TREATMENT\nSystemic chemotherapy :\nPREDNISOLONE 60 mg/m2 /day , oral or i.v. x 21 days ( 1 to "\
           "22 ) 30 mg/m2 /day , oral or i.v. x 7 days ( 23 to 29 )\nDAUNORUBICIN 30 mg/m2 , i.v. days 1 , 8 , " \
           "15 and 22\nVINCRISTINE 1 , 5 mg/m2 , i.v. days 1 , 8 , 15 and 22\nL-ASPARAGINASE 10.000U/m2 i.m or i.v " \
           "day 9 , 11 , 13 , 16 , 18 , 20 , 23 , 25 and 27\nCYCLOPHOSPHAMIDE 500 mg/m2 i.v. days 1 , " \
           "2 and 29\nIntrathecal chemotherapy :\nDays 1 and 22 according age :\nAge < 1 years 1-3 years > 3 " \
           "years\nMethotrexate ( MTX ) , mg 5 8 12 Ara-C , mg 16 20 30 Hydrocortisone , mg 10 10 20\nPatients with < "\
           "10% blasts in M.O ( day 14 ) , and in complete response on week 5 or 6 , and without MDR , " \
           "start consolidation-intensification phase.\nPatients with > 10% blasts in MO day +14 or without CR after " \
           "induction treatment , start consolidation-intensification phase and identifier a donor for a " \
           "transplantation.\nCONSOLIDATION/INTENSIFICATION ( C.I. )\nTwo sequential cycles , alternating bloc I and " \
           "bloc II\nBLOC I\nDEXAMETHASONE 10 mg/m2/d vo. days 1 to 5 and 5 mg/m2/d vo. days 6 and 7\nVINCRISTINE 1.5 "\
           "mg/m2/d , i.v. days 1 and 8\nMETHOTREXATE 5 g/m2 24 hours infusion + AF , day 1\nARA-C 1 g/m2/12 h , " \
           "i.v. , days 5 and 6\nMERCAPTOPURINE 100 mg/m2/d , oral , days 1 to 5\nCYCLOPHOSPHAMIDE 500 mg/m2 i.v. el " \
           "day +8\nINTRATHECAL CHEMOTHERAPY day 1.\nBLOC II\nDEXAMETHASONE 10 mg/m2/d , v o. days 1-5 and 5 mg/m2/d " \
           ", v o. days 6 and 7\nVINCRISTINE 1.5 mg/m2/d , days 1 and 8\nMETHOTREXATE 5 g/m2 24 h infusion + AF , " \
           "day 1\nARA-C 1 g/m2 i.v/12 h , days 5 and 6\nDAUNORUBICINE 30 mg/m2 i.v.day 1\nL-ASPARAGINASE 20.000 " \
           "u/m2/d , i.m. or i.v. day 7\nINTRATHECAL CHEMOTHERAPY day 1\nPatients with CR and MRD negative , " \
           "follow chemotherapy. Patients with MDR > 0.01% after second cycle or considered previously MRD are " \
           "candidates to allogenic transplantation after second cycle.\nREINDUCTION/INTENSIFICATION TREATMENT ( R.I. "\
           ")\nPREDNISOLONE 60 mg/m2/d , oral x 14 days ( 1-14 ) 30 mg/m2/d , oral x 7 days ( 15-22 )\nVINCRISTINE " \
           "1.5 mg/m2 , i.v. x 2 days 1 and 8\nDAUNORUBICINE 30 mg/m2 i.v x 2 , days 1 and 8\nCYCLOPHOSPHAMIDE 500 " \
           "mg/m2 I.V. day 15\n\nMETHOTREXATE 3 g/m2 /24 h infusion + AF day 29\nMERCAPTOPURINE 50 mg/m2/d , oral , " \
           "days 29-35 and 43-50\nARA-C 1 g/m2/12 h. , i.v. , days 43 and 44\nINTRATHECAL CHEMOTHERAPY , days 1 , " \
           "15 , 29 and 43\nMAINTENANACE TREATMENT ( M1 )\nSix cycles of :\nMERCAPTOPURINE 50 mg/m2/d , " \
           "oral x 21 days ( 1-21 )\nMETHOTREXATE 20 mg/m2/d , i.m. /week x 3 ( 1 , 7 , 14 )\nPREDNISOLONE 60 mg/m2/d "\
           ", oral x 7 days ( 22-28 )\nVINCRISTINE 1.5 mg/m2 i.v.day 22\nASPARAGINASE 20.000 u/m2 i.m. day " \
           "22\nINTRATHECAL CHEMOTHERAPY day 22\nMAINTENANCE TREATMENT ( M2 )\nDiary mercaptopurine and weekly " \
           "methotrexate at previous doses , until complete 24 months. "
    text2 = '''
        Patient: [** Name **], [** Name **]       Acct.#:     [** Medical_Record_Number **]       MR #:     [** Medical_Record_Number **]  
        D.O.B:   [** Date **]            Date of     [** Date **]        Location: [** Location **]  
                                       Visit:  
        Dictated [** Date **]  8:17 P    Transcribed [** Date **]  9:45  
        :                              :           P  
          
                                        CLINIC NOTE  
          
        DIAGNOSES:  
        1.  Lymphoplasmacytoid lymphoma involving bone marrow and spleen diagnosed  
        initially in [** Date **], associated with progressively increasing IgG kappa  
        paraprotein.  
        2.  Compression fractures of the spine secondary to lymphoma.  In the past,  
        it has been associated with significant back pain.  He is status post three  
        kyphoplasties.  The first in [** Date **] and two in [** Date **].  The first  
        procedure was complicated by acute hemoglobin decrease for which he was  
        hospitalized.  Hemorrhagic pericardial effusion was diagnosed and drained.  
        It was not malignant.  He received 5 units of red cells at that time.  
        2.  Extended hospitalization in [** Date **].  Then he was admitted for  
        significant back pain and then developed Salmonella sepsis with necrotizing  
        fasciitis of right gastrocnemius, which required debridement.  He had a  
        residual ulcer on the medial malleolus of the right ankle, which is now  
        fully healed.  He has required several hospitalizations for recurrent  
        cellulitis of right leg and most recently in [** Date **].  During the  
        prolonged hospitalization in [** Date **], he had respiratory arrest requiring  
        prolonged intubation and renal dialysis.  
        3.  Bilateral DVT with right leg DVT in [** Date **].  He finished 6-month  
        course of Coumadin after initially being treated with Lovenox.  
        4.  Psoriasis, which is quiescent.  
        5.  Hypertension.  
        6.  Hypothyroidism.  
        7.  Chronic renal insufficiency, which is multifactorial.  
          
        CURRENT THERAPY:  
        1.  He is on thalidomide 200 mg once daily for 2 weeks on and 2 weeks off.  
        He also takes prednisone 5 mg twice daily.  
        2.  Pamidronate 90 mg intravenously once a month.  
        3.  He has been on Velcade two weeks out of each month with reduced dosing  
        schedule of 1 mg/m2 once a week.  It was then discontinued secondary to  
        neuropathy.  It should be noted that did not respond to Velcade and  
        thalidomide.  
          
        PAST CHEMOTHERAPY:  
        1.  He has received 6 cycles of Rituxan plus CVP completed in [** Date **].  
        2.  Maintenance Rituxan completed in [** Date **].  
        3.  Revlimid, which was discontinued secondary to skin rash.  
        4.  Fludarabine in [** Date **], which rendered him profoundly  
        pancytopenic.  
          
        ADDITIONAL MEDICATIONS:  MS Contin 15 mg p.o. b.i.d., MSIR 30 mg every 4  
        hours for breakthrough pain.  Cartia XT, doxazosin, Protonix, Lasix,  
        Levoxyl, multivitamins and Neurontin 200 mg b.i.d.  He received his refills  
        for MS Contin and MSIR today.  
          
        INTERIM HISTORY:  Mr. [** Name **] returns for followup of his lymphoma.  He  
        recently sustained a fall secondary to slipping on ice.  He hurt his lower  
        back and has moderate, 4/10 back pain.  He is currently on MS Contin and  
        MSIR with relief of his symptoms.  He continues to have neuropathy from  
        Velcade, which is relieved with Neurontin 200 mg p.o. b.i.d.  He also has  
        constipation and is taking Colace 100 mg p.o. b.i.d. with relief of  
        symptoms.  
          
        He is also being followed by endocrinology for weight gain.  He has low  
        testosterone levels and has been started on replacement over the last 10  
        days.  
          
        REVIEW OF SYSTEMS:  He denies any history of fevers, night sweats, chills,  
        headache or visual blurring.  He denies any chest pain, cough, dyspnea,  
        orthopnea and no peripheral edema.  He denies any abdominal pain, nausea or  
        vomiting.  He has constipation.  He denies any episodes of diarrhea, bright  
        red blood per rectum or melena.  He has significant peripheral neuropathy  
        secondary to Velcade and is on Neurontin.  
          
        FAMILY HISTORY:  Acute leukemia in his father.  His father also had bladder  
        cancer.  He has one sibling who is not HLA match.  He has no family history  
        of lymphoma or multiple myeloma.  
          
        His ECOG performance status is 1, which is unchanged.  He is limited due to  
        back pain and cannot stand for prolonged periods of time.  He, however,  
        lives independently and is independent with all ADLs.  
          
        PHYSICAL EXAMINATION:  
        GENERAL:  He is alert and oriented x3.  
        VITAL SIGNS:  Stable.  Temperature 98.3, pulse 72, blood pressure 140/90,  
        respiratory rate 16 and weight is 117 kilograms.  No cervical,  
        supraclavicular or axillary lymphadenopathy.  
        LUNGS:  Clear to auscultation bilaterally.  
        CARDIOVASCULAR:  S1, S2 present, no murmurs.  
        ABDOMEN:  Soft, nontender and nondistended.  Good bowel sounds.  No  
        hepatosplenomegaly is palpable.  
        EXTREMITIES:  There is 2+ peripheral edema.  He is wearing compression  
        stocking on the right leg.  
        NEUROLOGICAL:  Nonfocal.  His gait is abnormal secondary to pain.  
          
        LABORATORY DATA:  WBC 3.7, hemoglobin 12.4, hematocrit 36.2, platelet count  
        is 143,000, BUN is 22, creatinine is 1.35, calcium is 9.4, kappa 328.39,  
        lambda light chain 1.46, ratio 224.92,  
        IgG 3580, which has increased from before.  
          
        ASSESSMENT AND PLAN:  Mr. [** Name **] is a 53-year-old male with  
        lymphoplasmacytoid lymphoma that is acting more like multiple myeloma and  
        affecting his bones.  His disease is currently stable.  He was better  
        controlled on Velcade, but developed significant peripheral neuropathy.  He  
        is getting better with Neurontin.  
          
        The patient is worried about losing his long-term disability.  He is unable  
        to stand for prolonged period of time and would like to return to work but  
        is unable to.  He will continue to receive Zometa once monthly.  He will  
        continue on thalidomide 100 mg once daily, 2 weeks on and 2 weeks off.  He  
        will also continue prednisone 5 mg twice daily.  
          
        He will follow up with Dr. [** Name **] at [** Hospital **].  He is  
        not a transplant candidate because his disease is minimally responsive to  
        chemotherapy.  He would be a good candidate for clinical trials.  
          
        He will follow up with us in 1 month.  
          
          
          
        I saw and evaluated the patient.  I discussed the case with the fellow and  
        agree with the findings and plan as documented in the fellow's note.  
          
        Reviewed  
        [** Name **] [** Name **], MD [** Date **] 16:26  
          
        E-Signed By  
        [** Name **] [** Name **] [** Name **], MD [** Date **] 18:49  
        ____________________________  
        [** Name **] [** Name **] [** Name **], MD  
          
        Patient evaluated by and note dictated by: [** Name **] [** Name **], MD  
          
        [** Medical_Record_Number **]  
          
        cc:    [** Name **] [** Name **], MD 
    '''

    text3 ='''
TITLE:\n   67 y.o.m. with metastatic renal cell carcinoma with metastasis to the\n   pancreas and liver as well as known duodenal/ampullary mass presents\n   with BRBPR x 2 days. Of note, the patient was recently started on\n   sutent. Pt states that he first noticed bloody bowel movement yesterday\n   am. He called his oncologist who recommended bowel prep in anticipation\n   of colonoscopy today given known side effect of bleeding with sutent.\n   Pt has colonoscopy this am that showed blood in colon but no\n   identifiable source. Pt was referred to the ED for tagged RBC scan and\n   labs.\n   Here, a tagged RBC scan was positive at 60 min, and pt was taken to\n   angiography. There, they couldn't find any obvious source of bleed, but\n   was consistent with a small bowel source.\n   HCT noted to drop further to 21 and patient was then referred for MICU\n   admission.\n   On admission, he denies fast heart rate, lightheadedness, dizziness,\n   chest or abdominal pain, tenesmus.  He feels generally well, though a\n   little anxious.\n   Status post left nephrectomy followed by high-dose IL-2 [**2166**].\n     st. post resection of residual renal bed mass in [**2168**]\n    Recurrence in the left renal fossa and pancreas in [**4-/2182**]\n    [**2185**], which showed progression of pancreatic metastases.  Perifosine\n   held since [**2187-6-13**] due to GI bleed.\n    ERCP on [**2187-6-20**] showed a malignant appearing mass in\n   duodenum, pathology consistent with metastatic renal cell Ca.\n    Perifosine restarted [**2187-6-27**] for one week, held on [**7-4**] due to\n   SBO requiring hospital admission in [**Hospital3 **], and\n   restarted again on [**7-11**].\n   Perifosine held due to elevated LFTs on [**2187-7-25**].\n    ERCP on [**2187-8-3**] - biliary stent placed to proximal CBD.\n   .H/O hypertension, benign\n   Assessment:\n   When pt is anxious & claustrophobic Bp once in 180\ns, Usually in 130\n   to 140\n   Action:\n   Anti Htn meds held. Anxiety treated with ativan.\n   Response:\n   BP continues to be in 120\ns to 140\ns. Pt calmer & less anxious after\n   ativan doses.\n   Plan:\n   Plan to start Nitroglycerin gtt if SBP above 180. continue monitoring\n   bp.\n   Anxiety\n   Assessment:\n   Pt states tthat he is claustrophobic when he is on bedrest & connected\n   to so mant wires & cannot take a walk around. Requesting doses of\n   ativan frequently to keep himself calm.\n   Action:\n   Total of 2 mgs iv ativan given & 0.5 mg of po ativan given. Orders for\n   prn ativan 0.5 mgs to 2 mgs\n   Response:\n   Pt slept off & on & is less anxious post ativan & waits for the next\n   dose to be given after he is awake from the previously given dose.\n   Emotional support given. TV & lights on as per patient comfort.\n   Plan:\n   Continue emotional support, Ativan as per orders.\n   .H/O liver function abnormalities\n   Assessment:\n   Labs awaited.\n   Action:\n   Response:\n   Plan:\n   .H/O gastrointestinal bleed, lower (Hematochezia, BRBPR, GI Bleed, GIB)\n   Assessment:\n   Pt came in with HCt of 21, Had one episode of large maroon stools. Seen\n   by surgery team & MICU Team.\n   Action:\n   3 units of blood given, 4^th ordered.\n   Response:\n   Hct ^ to 27 after the 3^rd unit of blood.\n   Plan:\n   Monitor labs, Blood as per orers.\n   Seen by surgery, Foley inserted to track urine output.\n   PLAN:\n    To support with blood products overnight, following serial coags / CBC\n   every 6-8 hours. To continue aggressive acid inhibition with IV PPI and\n   close communication with surgery, GI, and IR. Will check lactate and\n   LFTS / amylase / lipase to assess for occult hypoperfusion and\n   perforation. In the event of a catastrophic bleed, will retry IR\n   embolotherpy. Surgery might not be an option, and would certainly be\n   high risk. Will discuss with oncology and consider transfer to OMED\n   once stabilized.
       
    '''


    print(sent_tokenizer.sent_tokenizer(text1))
    print(sent_tokenizer.sent_tokenizer(text2))
    print(sent_tokenizer.sent_tokenizer(text3))


def test1():
    sent_tokenizer = SentenceBoundaryDetection()
    sent_tokenizer.set_deid_pattern("\[\*\*|\*\*\]")

    sent_tokenizer.set_input_file("../test/test_mimiciii_10/mimiciii_1.txt")
    print(sent_tokenizer.sent_word_tokenization_and_mapping())


def test2():
    # from file_utils.nlp_io import read_file
    # print(read_file('../../../2019amia_train/100-02.txt'))
    sent_tokenizer = SentenceBoundaryDetection()
    sent_tokenizer.set_deid_pattern("\[\*\*|\*\*\]")
    sent_tokenizer.special = True
    # sent_tokenizer.set_input_file("../../../2019amia_train/100-02.txt")
    # for each in sent_tokenizer.sent_word_tokenization_and_mapping():
    #     print(each)

    # text3 = '''TITLE:\n   67 y.o.m. with metastatic renal cell carcinoma with metastasis to the\n   pancreas and liver as well as known duodenal/ampullary mass presents\n   with BRBPR x 2 days. Of note, the patient was recently started on\n   sutent. Pt states that he first noticed bloody bowel movement yesterday\n   am. He called his oncologist who recommended bowel prep in anticipation\n   of colonoscopy today given known side effect of bleeding with sutent.\n   Pt has colonoscopy this am that showed blood in colon but no\n   identifiable source. Pt was referred to the ED for tagged RBC scan and\n   labs.\n   Here, a tagged RBC scan was positive at 60 min, and pt was taken to\n   angiography. There, they couldn't find any obvious source of bleed, but\n   was consistent with a small bowel source.\n   HCT noted to drop further to 21 and patient was then referred for MICU\n   admission.\n   On admission, he denies fast heart rate, lightheadedness, dizziness,\n   chest or abdominal pain, tenesmus.  He feels generally well, though a\n   little anxious.\n   Status post left nephrectomy followed by high-dose IL-2 [**2166**].\n     st. post resection of residual renal bed mass in [**2168**]\n    Recurrence in the left renal fossa and pancreas in [**4-/2182**]\n    [**2185**], which showed progression of pancreatic metastases.  Perifosine\n   held since [**2187-6-13**] due to GI bleed.\n    ERCP on [**2187-6-20**] showed a malignant appearing mass in\n   duodenum, pathology consistent with metastatic renal cell Ca.\n    Perifosine restarted [**2187-6-27**] for one week, held on [**7-4**] due to\n   SBO requiring hospital admission in [**Hospital3 **], and\n   restarted again on [**7-11**].\n   Perifosine held due to elevated LFTs on [**2187-7-25**].\n    ERCP on [**2187-8-3**] - biliary stent placed to proximal CBD.\n   .H/O hypertension, benign\n   Assessment:\n   When pt is anxious & claustrophobic Bp once in 180\ns, Usually in 130\n   to 140\n   Action:\n   Anti Htn meds held. Anxiety treated with ativan.\n   Response:\n   BP continues to be in 120\ns to 140\ns. Pt calmer & less anxious after\n   ativan doses.\n   Plan:\n   Plan to start Nitroglycerin gtt if SBP above 180. continue monitoring\n   bp.\n   Anxiety\n   Assessment:\n   Pt states tthat he is claustrophobic when he is on bedrest & connected\n   to so mant wires & cannot take a walk around. Requesting doses of\n   ativan frequently to keep himself calm.\n   Action:\n   Total of 2 mgs iv ativan given & 0.5 mg of po ativan given. Orders for\n   prn ativan 0.5 mgs to 2 mgs\n   Response:\n   Pt slept off & on & is less anxious post ativan & waits for the next\n   dose to be given after he is awake from the previously given dose.\n   Emotional support given. TV & lights on as per patient comfort.\n   Plan:\n   Continue emotional support, Ativan as per orders.\n   .H/O liver function abnormalities\n   Assessment:\n   Labs awaited.\n   Action:\n   Response:\n   Plan:\n   .H/O gastrointestinal bleed, lower (Hematochezia, BRBPR, GI Bleed, GIB)\n   Assessment:\n   Pt came in with HCt of 21, Had one episode of large maroon stools. Seen\n   by surgery team & MICU Team.\n   Action:\n   3 units of blood given, 4^th ordered.\n   Response:\n   Hct ^ to 27 after the 3^rd unit of blood.\n   Plan:\n   Monitor labs, Blood as per orers.\n   Seen by surgery, Foley inserted to track urine output.\n   PLAN:\n    To support with blood products overnight, following serial coags / CBC\n   every 6-8 hours. To continue aggressive acid inhibition with IV PPI and\n   close communication with surgery, GI, and IR. Will check lactate and\n   LFTS / amylase / lipase to assess for occult hypoperfusion and\n   perforation. In the event of a catastrophic bleed, will retry IR\n   embolotherpy. Surgery might not be an option, and would certainly be\n   high risk. Will discuss with oncology and consider transfer to OMED\n   once stabilized.'''
    # with open("/Users/alexgre/Downloads/note_14147.txt", "r") as f:
    #     text3 = f.read()
    # text3 = "L490R. AUCpinsulin E. coli E.coli IMPRESSION: AP chest compared to [**8-14**] through 11: Postoperative widening of the\n mediastinum is stable, as is bilateral subcutaneous emphysema and a small\n retrosternal air leak as seen before. Stable to slightly decreased size of the\n cardiomediastinal silhouette and presumed small-moderate pericardial effusion.\n There is slightly worse ill-defined right lower lobe atelectasis and small\n left lower lobe atelectasis and small bilateral pleural effusions."
  # print(sent_tokenizer.sent_tokenizer(text3))

    text3 = """intermittent A. Fib with temertet\n9. Toprol XL 50 mg Tablet Sustained Release 24 hr Sig: 1.5
Tablet Sustained Release 24 hrs PO once a day. Tablet Sustained
Release 24 hr(s)
10. Warfarin 5 mg Tablet Sig: One (1) Tablet PO Once Daily at 4
PM.
13. Insulin Glargine 100 unit/mL Cartridge Sig: Twenty Four (24)
units Subcutaneous at bedtime.
14. Pulmicort Flexhaler 180 mcg/Inhalation Aerosol Powdr Breath
Activated Sig: Two (2) puffs Inhalation twice a day.
20. Tamsulosin 0.4 mg Capsule, Sust. Release 24 hr Sig: One (1)
Capsule, Sust. Release 24 hr PO at bedtime. She will be discharged on her Metoprolol
Succinate, diovan, and her s p.o. b.i.d. Compazine 5 to 10 mg q.i.d.
p.r.n. nausea.
  Blood cultures from [**Doctor Last Name 1263**] grew out
[**4-26**] E. coli (with E. coli also in urine) resistant to
amp/pip/sulbactam
He is currently just on cipro and is to complete a 14 day course
for E. coli.  He continued to improve clinically, was extubated
on [**12-29**], """

    text3 = """T2aNxMx cT1cN0M0 T1cNxMx N0MXR0 pT3aNoMo
INCONTINENCE NOS|1   pT3bR1N0 as T10 He started stageT2cN0M0 T1N0m0
T2b/cNxM0
(see more details below).A"""

    normalized_txt, sents = sent_tokenizer.sent_word_tokenization_and_mapping(text3, max_len=100)
    print(normalized_txt)
    for each in sents:
        print(" ".join([e[0] for e in each]))


if __name__ == '__main__':
    test()
    test1()
    test2()
