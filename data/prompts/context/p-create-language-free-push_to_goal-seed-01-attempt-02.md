## Search State

- **Seed**: 1
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → push | linear_cartesian | linear_cartesian | position_control | admittance_control | pose_tolerance | pose_tolerance | 2 | 0.1758 | 0.24 | ❌ rejected |
| 1 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | contact_lost | 2 | 0.2464 | 0.22 | ❌ rejected |
| 0 | approach → push | linear_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 2 | 0.5140 | 0.43 | ✅ accepted |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`
- Frozen object start: [0.5014185949640309, 0.05405564355911223, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5014185949640309, 0.05405564355911223, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5014, 0.0541, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5014185949640309, 0.05405564355911223, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0014, -0.2041, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5014185949640309, 0.05405564355911223, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, -0.15, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.176) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: approach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.025
  weight: 0.4
- id: push_to_goal
  weight: 0.6
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.05
    - 0.025
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: approach_pre_contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.05, 0.025], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (add)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (add)

## Design Metrics

- **Composite score**: 0.176
- **task_score** (E): 0.245
- **fitness_score**: 0.276  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.100

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2373 |
| push_1 | 1.00 | 0.67 | 0.1571 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.479, 0.048, 0.072) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.479, 0.048, 0.072)→(0.497, -0.102, 0.035) | (0.474, -0.001, 0.025)→(0.502, -0.035, 0.035) | 0.154→0.116 | 0.67 / 1.667 | 0.479 | 168.450 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.399
- lateral_force_integral: None
- approach_alignment: 0.678
- goal_progress: 0.270
- terminal_score: 0.270
- phase_score: 0.312
- phase_breakdown.push_to_goal_score: 0.270
- phase_breakdown.approach_pre_contact_score: 0.374

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.295
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.270
- **Median Q (composite search score)**: 0.179
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Final σ (mean)**: 0.275


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f21cc79f03d9e871b86947069440973ee7e2ef557ebaac0b26b4f6cbdabf5bb1`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec03d65db90cc6b4602194a1eefa4c3104517a971e566e099fb50a3df7102251`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50142,0.05406,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.86885,"average_solve_count":61.0,"average_success_count":61.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.19946,"push_1.push_speed":0.17162},"optimized_scores":{"best_composite_score":0.17932,"best_fitness_score":0.27932,"best_task_score":0.24888},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":34.0,"contact_point_centroid":[0.5066,0.02457,0.04939],"force_p95":91.65033,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.62872,"mean_force":52.47646,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49933,0.01661,0.05054]},{"body_a":"world","body_b":"push_box","contact_count":486.0,"contact_point_centroid":[0.50259,0.0318,-0.00026],"force_p95":29.85601,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.49288,"mean_force":4.09905,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49835,0.01313,0.04897]},{"body_a":"world","body_b":"push_box","contact_count":880.0,"contact_point_centroid":[0.50142,0.05406,-0.0],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50103,0.045,0.18765]}],"total_contact_groups":3},"final_pose_error":0.04957,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5033,0.00324,0.02441],"final_tcp_position":[0.49903,-0.10062,0.02918],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":102.62872,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":220.0,"n_steps_budget":930.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":880.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_pre_contact","tcp_end":[0.50102,0.09351,0.06942],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":191.0,"n_steps_budget":900.0,"object_pos_end":[0.5033,0.00324,0.02441],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.15327,"object_to_goal_dist_start":0.20406,"object_z_max":0.03536,"peak_contact_force":0.27102,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":520.0,"raw_peak_contact_force":102.62872,"subtask_id":"push_to_goal","tcp_end":[0.49903,-0.10062,0.02918],"tcp_start":[0.50102,0.09351,0.06942],"tcp_to_object_dist_end":0.10405,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `060d405a872aae8d4597ed6284dedb60e9c99f80071c0520b1a8a2986f3c114d`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43165,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.08772,"push_1.push_speed":0.05132},"optimized_scores":{"best_composite_score":0.19479,"best_fitness_score":0.29479,"best_task_score":0.26962},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":375.0,"contact_point_centroid":[0.4766,-0.03009,-0.00023],"force_p95":201.86104,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":214.09973,"mean_force":28.86289,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47946,-0.00804,0.0578]},{"body_a":"attachment","body_b":"push_box","contact_count":75.0,"contact_point_centroid":[0.49784,-0.04899,0.04913],"force_p95":210.32686,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":212.96803,"mean_force":142.35958,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4918,-0.05783,0.04949]},{"body_a":"push_box","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.51472,-0.0638,0.08354],"force_p95":1.40641,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.41911,"mean_force":1.2921,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49841,-0.10147,0.03935]},{"body_a":"world","body_b":"push_box","contact_count":852.0,"contact_point_centroid":[0.47139,-0.02418,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4893,0.01361,0.19179]}],"total_contact_groups":4},"final_pose_error":0.04912,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50702,-0.05749,0.04156],"final_tcp_position":[0.49841,-0.10287,0.03878],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":214.09973,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":852.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_pre_contact","tcp_end":[0.47637,0.02882,0.07336],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":157.0,"n_steps_budget":1000.0,"object_pos_end":[0.50702,-0.05749,0.04156],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.09424,"object_to_goal_dist_start":0.12903,"object_z_max":0.04247,"peak_contact_force":1.16508,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":452.0,"raw_peak_contact_force":214.09973,"subtask_id":"push_to_goal","tcp_end":[0.49841,-0.10287,0.03878],"tcp_start":[0.47637,0.02882,0.07336],"tcp_to_object_dist_end":0.04628,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c4af277909bfbef2010e50829d2192ea184fe34d7420833f45dd73455a81c9b6`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93396,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07616,"push_1.push_speed":0.12627},"optimized_scores":{"best_composite_score":0.15343,"best_fitness_score":0.25343,"best_task_score":0.2156},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":361.0,"contact_point_centroid":[0.45459,-0.03631,-0.00015],"force_p95":167.63512,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":188.62162,"mean_force":19.74022,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46749,-0.0165,0.05707]},{"body_a":"attachment","body_b":"push_box","contact_count":55.0,"contact_point_centroid":[0.48343,-0.0518,0.04837],"force_p95":183.68179,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":186.97158,"mean_force":127.14789,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48324,-0.063,0.04764]},{"body_a":"world","body_b":"push_box","contact_count":860.0,"contact_point_centroid":[0.45028,-0.03158,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48123,0.01077,0.19202]}],"total_contact_groups":3},"final_pose_error":0.04917,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49451,-0.05028,0.03823],"final_tcp_position":[0.49367,-0.103,0.03796],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":188.62162,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":215.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":860.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_pre_contact","tcp_end":[0.45945,0.02292,0.0731],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":142.0,"n_steps_budget":930.0,"object_pos_end":[0.49451,-0.05028,0.03823],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.10074,"object_to_goal_dist_start":0.12843,"object_z_max":0.03936,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":416.0,"raw_peak_contact_force":188.62162,"subtask_id":"push_to_goal","tcp_end":[0.49367,-0.103,0.03796],"tcp_start":[0.45945,0.02292,0.0731],"tcp_to_object_dist_end":0.05272,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```