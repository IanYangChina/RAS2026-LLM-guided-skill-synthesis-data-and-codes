## Search State

- **Seed**: 1
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6934 | 0.88 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6057 | 0.89 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7644 | 0.83 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.3911 | 0.42 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5894 | 0.86 | ✅ accepted |

**Proposal policy**: task_score is 0.88 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.892, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=0.693) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: contact_1
  type: contact
  generator: impedance_motion
  control: force_threshold_switch
  termination: force_exceeded
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.693
- **task_score** (E): 0.882
- **fitness_score**: 0.787  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2822 |
| contact_1 | 0.67 | 1.00 | 0.0367 |
| push_1 | 1.00 | 1.00 | 0.1514 |
| retract_1 | 0.00 | 1.00 | 0.1169 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.472, 0.075, 0.033) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.67 / force_exceeded | (0.472, 0.075, 0.033)→(0.469, 0.040, 0.023) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.667 | 25303.881 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.469, 0.040, 0.023)→(0.495, -0.107, 0.020) | (0.474, -0.001, 0.025)→(0.492, -0.144, 0.025) | 0.154→0.019 | 1.00 / 3.333 | 6.176 | 47.654 |
| retract_1 | retract | 0.00 / step_budget | (0.495, -0.107, 0.020)→(0.493, -0.016, 0.093) | (0.492, -0.144, 0.025)→(0.492, -0.145, 0.025) | 0.019→0.019 | 1.00 / 4.000 | 0.245 | 0.936 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.566
- goal_progress: 0.865
- terminal_score: 0.865
- phase_score: 0.825
- phase_breakdown.approach_score: 0.822
- phase_breakdown.push_score: 0.860
- phase_breakdown.contact_score: 0.770

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.841
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.916
- **Median Q (composite search score)**: 0.703
- **K-run variance**: 0.0136
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.230


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53571,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15021,"contact_1.speed":0.0343,"push_1.push_distance":0.15773,"retract_1.speed":0.05849},"optimized_scores":{"best_composite_score":0.70308,"best_fitness_score":0.71308,"best_task_score":0.86484},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1400.0,"contact_point_centroid":[0.50181,-0.04355,-7e-05],"force_p95":44.79419,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.35839,"mean_force":11.05165,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49453,0.00434,0.01937]},{"body_a":"attachment","body_b":"push_box","contact_count":937.0,"contact_point_centroid":[0.50385,-0.00625,0.03621],"force_p95":37.48085,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.2685,"mean_force":11.49339,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49452,0.00525,0.01937]},{"body_a":"push_box","body_b":"link7","contact_count":387.0,"contact_point_centroid":[0.52166,0.028,0.05158],"force_p95":32.90629,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.7763,"mean_force":20.31193,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49449,0.04931,0.01962]},{"body_a":"world","body_b":"push_box","contact_count":3980.0,"contact_point_centroid":[0.49982,-0.12243,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75258,"mean_force":0.2465,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4925,-0.04172,0.05776]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.4993,-0.09641,0.02749],"force_p95":0.47497,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51258,"mean_force":0.30266,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49542,-0.08447,0.01976]},{"body_a":"world","body_b":"push_box","contact_count":3976.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49774,0.06374,0.16404]},{"body_a":"world","body_b":"push_box","contact_count":2420.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49494,0.10808,0.0242]}],"total_contact_groups":7},"final_pose_error":0.15678,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49978,-0.12242,0.02499],"final_tcp_position":[0.4935,0.00376,0.09385],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":994.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3976.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49731,0.12754,0.03129],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07387,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":605.0,"n_steps_budget":900.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2420.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49605,0.09101,0.02164],"tcp_start":[0.49731,0.12754,0.03129],"tcp_to_object_dist_end":0.03749,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50012,-0.12121,0.02503],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.02879,"object_to_goal_dist_start":0.20406,"object_z_max":0.02851,"peak_contact_force":1.69525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2724.0,"raw_peak_contact_force":58.35839,"tcp_end":[0.49548,-0.08433,0.01979],"tcp_start":[0.49605,0.09101,0.02164],"tcp_to_object_dist_end":0.03754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49978,-0.12242,0.02499],"object_pos_start":[0.50012,-0.12121,0.02503],"object_to_goal_dist_end":0.02758,"object_to_goal_dist_start":0.02879,"object_z_max":0.02512,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3984.0,"raw_peak_contact_force":0.75258,"tcp_end":[0.4935,0.00376,0.09385],"tcp_start":[0.49548,-0.08433,0.01979],"tcp_to_object_dist_end":0.14388,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47273,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.2539,"contact_1.speed":0.03606,"push_1.push_distance":0.10743,"retract_1.speed":0.04958},"optimized_scores":{"best_composite_score":0.83095,"best_fitness_score":0.84095,"best_task_score":0.86479},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1287.0,"contact_point_centroid":[0.48351,-0.10479,-7e-05],"force_p95":35.69084,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.49547,"mean_force":7.78935,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48036,-0.06042,0.01989]},{"body_a":"attachment","body_b":"push_box","contact_count":727.0,"contact_point_centroid":[0.48543,-0.06465,0.03149],"force_p95":30.56654,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.81975,"mean_force":10.62573,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47878,-0.05288,0.01991]},{"body_a":"push_box","body_b":"link7","contact_count":243.0,"contact_point_centroid":[0.49816,-0.03619,0.05112],"force_p95":23.59073,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.11405,"mean_force":14.56938,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47059,-0.01269,0.02034]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.48603,-0.16045,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50697,"mean_force":0.24566,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49158,-0.07839,0.05613]},{"body_a":"world","body_b":"push_box","contact_count":3424.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48366,0.02611,0.16637]},{"body_a":"world","body_b":"push_box","contact_count":2604.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.466,0.03169,0.02627]}],"total_contact_groups":6},"final_pose_error":0.18956,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48603,-0.16045,0.02499],"final_tcp_position":[0.49265,-0.03011,0.09135],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":51.49547,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":856.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3424.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.46886,0.05266,0.03395],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":651.0,"n_steps_budget":930.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":17.86254,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2604.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.46663,0.01278,0.0227],"tcp_start":[0.46886,0.05266,0.03395],"tcp_to_object_dist_end":0.03734,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":839.0,"n_steps_budget":930.0,"object_pos_end":[0.48615,-0.16007,0.02484],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.01712,"object_to_goal_dist_start":0.12903,"object_z_max":0.02956,"peak_contact_force":16.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2257.0,"raw_peak_contact_force":51.49547,"tcp_end":[0.49445,-0.12403,0.01996],"tcp_start":[0.46663,0.01278,0.0227],"tcp_to_object_dist_end":0.0373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48603,-0.16045,0.02499],"object_pos_start":[0.48615,-0.16007,0.02484],"object_to_goal_dist_end":0.01745,"object_to_goal_dist_start":0.01712,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.50697,"tcp_end":[0.49265,-0.03011,0.09135],"tcp_start":[0.49445,-0.12403,0.01996],"tcp_to_object_dist_end":0.14641,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20556,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18378,"contact_1.speed":0.0153,"push_1.push_distance":0.08989,"retract_1.speed":0.05284},"optimized_scores":{"best_composite_score":0.54626,"best_fitness_score":0.80626,"best_task_score":0.91597},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":680.0,"contact_point_centroid":[0.47153,-0.06473,0.02499],"force_p95":16.61797,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.10863,"mean_force":4.60929,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46929,-0.05281,0.02074]},{"body_a":"world","body_b":"push_box","contact_count":1676.0,"contact_point_centroid":[0.46823,-0.08725,-5e-05],"force_p95":6.89019,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.6658,"mean_force":2.14977,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46688,-0.04597,0.0211]},{"body_a":"world","body_b":"push_box","contact_count":3958.0,"contact_point_centroid":[0.48919,-0.15155,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.54697,"mean_force":0.24842,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49089,-0.06852,0.05721]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.4922,-0.12597,0.02084],"force_p95":1.46445,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.46445,"mean_force":1.46445,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49359,-0.11408,0.02017]},{"body_a":"world","body_b":"push_box","contact_count":3404.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47375,0.02263,0.1666]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44545,0.02911,0.0275]}],"total_contact_groups":6},"final_pose_error":0.18075,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48935,-0.15172,0.02499],"final_tcp_position":[0.49216,-0.02112,0.09231],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":33.10863,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":851.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3404.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44887,0.04566,0.03429],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4456,0.01649,0.02508],"tcp_start":[0.44887,0.04566,0.03429],"tcp_to_object_dist_end":0.0483,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":837.0,"n_steps_budget":930.0,"object_pos_end":[0.48954,-0.15085,0.02505],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.01049,"object_to_goal_dist_start":0.12843,"object_z_max":0.02534,"peak_contact_force":0.83167,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2356.0,"raw_peak_contact_force":33.10863,"tcp_end":[0.49359,-0.11408,0.02017],"tcp_start":[0.4456,0.01649,0.02508],"tcp_to_object_dist_end":0.03731,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48935,-0.15172,0.02499],"object_pos_start":[0.48954,-0.15085,0.02505],"object_to_goal_dist_end":0.01079,"object_to_goal_dist_start":0.01049,"object_z_max":0.02506,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3959.0,"raw_peak_contact_force":1.54697,"tcp_end":[0.49216,-0.02112,0.09231],"tcp_start":[0.49359,-0.11408,0.02017],"tcp_to_object_dist_end":0.14695,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```