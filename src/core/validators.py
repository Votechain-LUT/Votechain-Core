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


# mockup
def is_vvpat_valid(token, poll_id, decrypted_poll_id, decrypted_vote_id):
    """ validates a vote trail against a poll """
    if poll_id != decrypted_poll_id:
        return False
    trail = Trail.objects.filter(trail_token=token).first()
    if trail is None or trail.vote.id != decrypted_vote_id:
        return False
    if trail.vote.answer.poll.id != poll_id:
        return False
    return True
