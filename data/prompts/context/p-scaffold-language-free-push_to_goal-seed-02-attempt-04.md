## Search State

- **Seed**: 2
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5887 | 0.74 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0782 | 0.15 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.2441 | 0.00 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0581 | 0.01 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5898 | 0.76 | ✅ accepted |

**Proposal policy**: task_score is 0.74 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`
- Frozen object start: [0.47139345610991795, -0.0241810627903052, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.47139345610991795, -0.0241810627903052, 0.025)
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
  frozen_object_start: [0.4714, -0.0242, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.47139345610991795, -0.0241810627903052, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0286, -0.1258, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.756, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.47139345610991795, -0.0241810627903052, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.589) — your mutation base

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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: impedance_motion
  control: admittance_control
  termination: contact_detected
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

```

## Design Metrics

- **Composite score**: 0.589
- **task_score** (E): 0.741
- **fitness_score**: 0.799  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2775 |
| contact_1 | 1.00 | 1.00 | 0.0490 |
| push_1 | 1.00 | 1.00 | 0.1391 |
| retract_1 | 0.00 | 1.00 | 0.1675 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.488, 0.058, 0.033) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.488, 0.058, 0.033)→(0.487, 0.011, 0.021) | (0.492, -0.018, 0.025)→(0.493, -0.026, 0.025) | 0.139→0.132 | 1.00 / 2.000 | 0.926 | 12.943 |
| push_1 | push | 1.00 / step_budget | (0.487, 0.011, 0.021)→(0.499, -0.122, 0.023) | (0.493, -0.026, 0.025)→(0.494, -0.145, 0.027) | 0.132→0.039 | 1.00 / 3.000 | 43.654 | 83.744 |
| retract_1 | retract | 0.00 / step_budget | (0.499, -0.122, 0.023)→(0.496, 0.017, 0.116) | (0.494, -0.145, 0.027)→(0.490, -0.143, 0.025) | 0.039→0.036 | 1.00 / 4.000 | 0.245 | 25.946 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.454
- goal_progress: 0.800
- terminal_score: 0.800
- phase_score: 0.846
- phase_breakdown.contact_score: 0.869
- phase_breakdown.push_score: 0.844
- phase_breakdown.approach_score: 0.819

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.828
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.800
- **Median Q (composite search score)**: 0.584
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.143


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `27920116be2b9a598fe307ae470bb0295293d051bb1ef513a0996a4d851f2459`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1a1e2536715050e6c37d8aed13e4ecd62004f6234f1413b07d7b475a233f55c9`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56977,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19038,"approach_1.speed":0.06723,"push_1.push_distance":0.09698},"optimized_scores":{"best_composite_score":0.61763,"best_fitness_score":0.82763,"best_task_score":0.7996},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1204.0,"contact_point_centroid":[0.48347,-0.11113,-0.0001],"force_p95":48.1997,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.5084,"mean_force":10.70302,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48179,-0.06686,0.01945]},{"body_a":"attachment","body_b":"push_box","contact_count":647.0,"contact_point_centroid":[0.48674,-0.06446,0.03366],"force_p95":34.91591,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.16384,"mean_force":13.74985,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47884,-0.05278,0.01953]},{"body_a":"push_box","body_b":"link7","contact_count":283.0,"contact_point_centroid":[0.49907,-0.04173,0.0511],"force_p95":32.91346,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.45271,"mean_force":22.48389,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47184,-0.01803,0.02002]},{"body_a":"attachment","body_b":"push_box","contact_count":84.0,"contact_point_centroid":[0.47442,-0.00283,0.03481],"force_p95":10.65672,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.78494,"mean_force":3.79478,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4669,0.00903,0.0221]},{"body_a":"world","body_b":"push_box","contact_count":1899.0,"contact_point_centroid":[0.47148,-0.02535,-1e-05],"force_p95":1.23852,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.91249,"mean_force":0.41828,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46618,0.03054,0.02626]},{"body_a":"world","body_b":"push_box","contact_count":3972.0,"contact_point_centroid":[0.47464,-0.15505,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76614,"mean_force":0.24644,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49205,-0.05445,0.07064]},{"body_a":"world","body_b":"push_box","contact_count":3608.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48365,0.02607,0.16656]}],"total_contact_groups":7},"final_pose_error":0.13858,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47464,-0.15505,0.02499],"final_tcp_position":[0.49372,0.01636,0.11387],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":63.5084,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":902.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3608.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.46887,0.05263,0.03409],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.47284,-0.03174,0.0251],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12134,"object_to_goal_dist_start":0.12903,"object_z_max":0.02511,"peak_contact_force":1.51552,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1983.0,"raw_peak_contact_force":11.78494,"tcp_end":[0.46712,0.00513,0.02143],"tcp_start":[0.46887,0.05263,0.03409],"tcp_to_object_dist_end":0.03749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":782.0,"n_steps_budget":870.0,"object_pos_end":[0.47585,-0.15381,0.0251],"object_pos_start":[0.47284,-0.03174,0.0251],"object_to_goal_dist_end":0.02445,"object_to_goal_dist_start":0.12134,"object_z_max":0.03037,"peak_contact_force":0.41047,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2134.0,"raw_peak_contact_force":63.5084,"tcp_end":[0.49431,-0.12132,0.01987],"tcp_start":[0.46712,0.00513,0.02143],"tcp_to_object_dist_end":0.03774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47464,-0.15505,0.02499],"object_pos_start":[0.47585,-0.15381,0.0251],"object_to_goal_dist_end":0.02586,"object_to_goal_dist_start":0.02445,"object_z_max":0.0253,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.76614,"tcp_end":[0.49372,0.01636,0.11387],"tcp_start":[0.49431,-0.12132,0.01987],"tcp_to_object_dist_end":0.19402,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e864853e179d3df1b19d9aaa17e18a5fe8c66fe7533fc0dd3a88a693de7416e7`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27184,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16013,"approach_1.speed":0.02991,"push_1.push_distance":0.09015},"optimized_scores":{"best_composite_score":0.56459,"best_fitness_score":0.77459,"best_task_score":0.67038},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1285.0,"contact_point_centroid":[0.46072,-0.10993,-7e-05],"force_p95":35.87401,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.96883,"mean_force":7.45161,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4723,-0.07092,0.01956]},{"body_a":"attachment","body_b":"push_box","contact_count":636.0,"contact_point_centroid":[0.47317,-0.06789,0.0328],"force_p95":27.65159,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.79257,"mean_force":10.40261,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4667,-0.05643,0.01965]},{"body_a":"push_box","body_b":"link7","contact_count":255.0,"contact_point_centroid":[0.48092,-0.04448,0.05064],"force_p95":23.09587,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.90545,"mean_force":16.9263,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45367,-0.02212,0.02007]},{"body_a":"attachment","body_b":"push_box","contact_count":81.0,"contact_point_centroid":[0.45166,-0.01025,0.03099],"force_p95":11.26319,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.10783,"mean_force":3.80063,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44606,0.00166,0.02246]},{"body_a":"world","body_b":"push_box","contact_count":1938.0,"contact_point_centroid":[0.45025,-0.03249,-1e-05],"force_p95":1.0973,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.75998,"mean_force":0.40602,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44582,0.02297,0.02667]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48661,-0.13191,0.02291],"force_p95":4.08196,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.08196,"mean_force":4.08196,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49318,-0.12236,0.01982]},{"body_a":"world","body_b":"push_box","contact_count":3983.0,"contact_point_centroid":[0.45842,-0.14179,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.92028,"mean_force":0.24665,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49126,-0.05529,0.07057]},{"body_a":"world","body_b":"push_box","contact_count":3712.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47374,0.02259,0.16679]}],"total_contact_groups":8},"final_pose_error":0.13898,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45848,-0.14174,0.02499],"final_tcp_position":[0.4932,0.01595,0.11396],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":48.96883,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":928.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3712.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4489,0.04564,0.03445],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.45136,-0.03902,0.02506],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12118,"object_to_goal_dist_start":0.12843,"object_z_max":0.02508,"peak_contact_force":0.18606,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2019.0,"raw_peak_contact_force":15.10783,"tcp_end":[0.44621,-0.0022,0.02179],"tcp_start":[0.4489,0.04564,0.03445],"tcp_to_object_dist_end":0.03732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.4591,-0.1414,0.02497],"object_pos_start":[0.45136,-0.03902,0.02506],"object_to_goal_dist_end":0.0418,"object_to_goal_dist_start":0.12118,"object_z_max":0.03213,"peak_contact_force":0.00033,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2176.0,"raw_peak_contact_force":48.96883,"tcp_end":[0.49324,-0.12224,0.01986],"tcp_start":[0.44621,-0.0022,0.02179],"tcp_to_object_dist_end":0.03948,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45848,-0.14174,0.02499],"object_pos_start":[0.4591,-0.1414,0.02497],"object_to_goal_dist_end":0.04233,"object_to_goal_dist_start":0.0418,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3984.0,"raw_peak_contact_force":4.08196,"tcp_end":[0.4932,0.01595,0.11396],"tcp_start":[0.49324,-0.12224,0.01986],"tcp_to_object_dist_end":0.18435,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c820cf29ab3e34ea9695cb40d5aba5de55f3ad951ee91f0df578ae7146ee7727`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7987,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22473,"approach_1.speed":0.09949,"push_1.push_distance":0.13591},"optimized_scores":{"best_composite_score":0.58385,"best_fitness_score":0.79385,"best_task_score":0.75346},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":987.0,"contact_point_centroid":[0.56313,-0.05832,0.05455],"force_p95":130.29439,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.75398,"mean_force":87.36736,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52812,-0.04623,0.02423]},{"body_a":"world","body_b":"push_box","contact_count":1915.0,"contact_point_centroid":[0.56044,-0.09151,-0.00038],"force_p95":100.84889,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":111.81367,"mean_force":57.72093,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5278,-0.04791,0.02443]},{"body_a":"attachment","body_b":"push_box","contact_count":995.0,"contact_point_centroid":[0.54812,-0.05294,0.05479],"force_p95":90.76143,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.49177,"mean_force":57.6345,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52829,-0.0456,0.0242]},{"body_a":"push_box","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.55142,-0.12625,0.05685],"force_p95":47.54813,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.98893,"mean_force":20.94427,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50854,-0.12139,0.0307]},{"body_a":"world","body_b":"push_box","contact_count":3601.0,"contact_point_centroid":[0.53753,-0.13306,-2e-05],"force_p95":0.45211,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.40664,"mean_force":0.45006,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50347,-0.04839,0.08227]},{"body_a":"attachment","body_b":"push_box","contact_count":94.0,"contact_point_centroid":[0.52977,-0.11654,0.05961],"force_p95":28.79159,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.90017,"mean_force":6.93275,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50695,-0.11403,0.03557]},{"body_a":"attachment","body_b":"push_box","contact_count":91.0,"contact_point_centroid":[0.5535,0.02259,0.03708],"force_p95":10.0368,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.93718,"mean_force":3.23661,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54759,0.03453,0.02028]},{"body_a":"world","body_b":"push_box","contact_count":1890.0,"contact_point_centroid":[0.5531,-0.00037,-1e-05],"force_p95":1.00839,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.34893,"mean_force":0.40674,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54519,0.05588,0.02339]},{"body_a":"world","body_b":"push_box","contact_count":3804.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52233,0.03845,0.16442]}],"total_contact_groups":9},"final_pose_error":0.13486,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53556,-0.13269,0.02499],"final_tcp_position":[0.50126,0.01873,0.11909],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":138.75398,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":951.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3804.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54657,0.0772,0.03118],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07638,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.55473,-0.0065,0.025],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15358,"object_to_goal_dist_start":0.16043,"object_z_max":0.02513,"peak_contact_force":1.07688,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1981.0,"raw_peak_contact_force":11.93718,"tcp_end":[0.54816,0.0304,0.01979],"tcp_start":[0.54657,0.0772,0.03118],"tcp_to_object_dist_end":0.03784,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54851,-0.14055,0.03066],"object_pos_start":[0.55473,-0.0065,0.025],"object_to_goal_dist_end":0.04975,"object_to_goal_dist_start":0.15358,"object_z_max":0.03107,"peak_contact_force":130.55006,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3897.0,"raw_peak_contact_force":138.75398,"tcp_end":[0.50986,-0.12359,0.02924],"tcp_start":[0.54816,0.0304,0.01979],"tcp_to_object_dist_end":0.04223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53556,-0.13269,0.02499],"object_pos_start":[0.54851,-0.14055,0.03066],"object_to_goal_dist_end":0.03955,"object_to_goal_dist_start":0.04975,"object_z_max":0.03277,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3737.0,"raw_peak_contact_force":72.98893,"tcp_end":[0.50126,0.01873,0.11909],"tcp_start":[0.50986,-0.12359,0.02924],"tcp_to_object_dist_end":0.18155,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```