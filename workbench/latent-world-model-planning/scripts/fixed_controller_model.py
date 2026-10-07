"""H2 causal composition state includes the predicted issued-action history."""
import torch
import intact_published_control_v3 as a
import controller_outcome_features as f

TRAIN = list(range(16))+list(range(24, 40))
HELD = list(range(16, 24))+list(range(40, 48))
METHODS = ['OPEN25', 'GOAL5']


def option(world, policy, head, current, goal, previous, method):
    """Return five prefix states and five predicted command macros.

    For direct feedback outcomes, the original actor converts predicted real
    prefix states into future commands recursively. These are imagined history,
    not recorded commands and not the commands issued at real deployment.
    The original OPEN policy plan is formed with its original world throughout.
    """
    is_open = method == 'OPEN25'
    base_z, base_actions = current[:, None], previous[:, None]
    plan = []
    if is_open:
        for _ in range(5):
            action = f.actor(policy, base_z, goal, base_actions)
            plan.append(action)
            base_z, base_actions = f.step(policy, base_z, base_actions, action)
    if head is not None:
        kinds = torch.full((len(current),), 0 if is_open else 1, dtype=torch.long, device=current.device)
        predicted = head(current, goal, previous, kinds)
        z, actions, issued = current, previous, []
        for k in range(5):
            command = plan[k] if is_open else f.actor(policy, z[:, None], goal, actions[:, None])
            issued.append(command)
            z, actions = predicted[:, k], command
        return predicted, torch.stack(issued, 1)
    if is_open and world is policy:
        return base_z[:, 1:], torch.stack(plan, 1)
    z, actions, states, issued = current[:, None], previous[:, None], [], []
    for k in range(5):
        command = plan[k] if is_open else f.actor(policy, z, goal, actions)
        z, actions = f.step(world, z, actions, command)
        states.append(z[:, -1])
        issued.append(command)
    return torch.stack(states, 1), torch.stack(issued, 1)


def load_weights(task, arm, complete, device='cuda'):
    net, processor, source = a.source(task, device)
    head = None
    if arm != 'FROZEN-WORLD':
        payload = torch.load(complete['checkpoint'], map_location='cpu', weights_only=True)
        assert payload['source'] == source and payload['task'] == task and payload['arm'] == arm
        if arm == 'DIRECT-CONTROLLER':
            from controller_outcome_train import Outcome
            head = Outcome(payload['center'], payload['scale'])
            head.load_state_dict(payload['state'], strict=True)
            head = head.to(device).eval().requires_grad_(False)
        else:
            full = net.state_dict()
            assert set(payload['state']) == {k for k in full if k.startswith(('predictor.', 'pred_proj.'))}
            full.update(payload['state'])
            net.load_state_dict(full, strict=True)
    return net, head, processor, source
