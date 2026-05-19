from django.urls import reverse
from assessments.models import Assessment


def build_stage_context(journey):
    """
    Builds the stage configuration list for the journey detail view.
    Returns a list of stage dicts consumed by the template loop.
    """
    assessments_qs = (
        journey.assessments
        .select_related('result')
        .prefetch_related('doctor_notes')
        .all()
    )

    assessments = {a.stage: a for a in assessments_qs}

    s1 = assessments.get(Assessment.Stage.STAGE_1)
    s2 = assessments.get(Assessment.Stage.STAGE_2)
    s3 = assessments.get(Assessment.Stage.STAGE_3)

    stages = [
        {
            'key':                'S1',
            'label':              'Symptomatic',
            'assessment':         s1,
            'prev_done':          True,
            'show_doctor_confirm': False,
            'show_clinic_confirm': True,
            'begin_url':          reverse('create_assessment', args=[journey.pk, 'Stage_1']),
            'locked_message':     '',
        },
        {
            'key':                'S2',
            'label':              'Clinical',
            'assessment':         s2,
            'prev_done':          s1 is not None,
            'show_doctor_confirm': not journey.doctor,
            'show_clinic_confirm': False,
            'begin_url':          None,
            'locked_message':     'Adding bloodwork results will refine your risk profile and unlock specialist matching.',
        },
        {
            'key':                'S3',
            'label':              'Imaging',
            'assessment':         s3,
            'prev_done':          s2 is not None,
            'show_doctor_confirm': False,
            'show_clinic_confirm': False,
            'begin_url':          None,
            'locked_message':     'Imaging data (ultrasound, follicle counts) will be entered by your assigned specialist after your scan.',
        },
    ]

    return stages