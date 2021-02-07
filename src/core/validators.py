from core.models.models import Trail


def is_vit_valid(vit, poll):
    """ validates a vit against a poll """
    if vit is None or poll is None:
        return False
    if vit.poll.id != poll.id:
        return False
    if vit.used:
        return False
    return True
