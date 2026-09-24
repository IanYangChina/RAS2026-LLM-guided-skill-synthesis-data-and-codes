## Search State

- **Seed**: 8
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | 0.4443 | 0.76 | ✅ accepted |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`
- Frozen object start: [0.4792366731926673, 0.05847322120055107, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.4792366731926673, 0.05847322120055107, 0.025)
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
  frozen_object_start: [0.4792, 0.0585, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.4792366731926673, 0.05847322120055107, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0208, -0.2085, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.755, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.4792366731926673, 0.05847322120055107, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.444) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.444
- **task_score** (E): 0.755
- **fitness_score**: 0.754  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2844 |
| contact_1 | 1.00 | 1.00 | 0.0483 |
| push_1 | 0.67 | 1.00 | 0.1422 |
| retract_1 | 0.00 | 1.00 | 0.1267 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, 0.075, 0.032) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.521, 0.075, 0.032)→(0.521, 0.028, 0.020) | (0.526, -0.001, 0.025)→(0.528, -0.008, 0.025) | 0.156→0.150 | 1.00 / 3.000 | 3.389 | 12.541 |
| push_1 | push | 0.67 / step_budget | (0.521, 0.028, 0.020)→(0.503, -0.110, 0.026) | (0.528, -0.008, 0.025)→(0.525, -0.139, 0.029) | 0.150→0.039 | 1.00 / 3.000 | 77.658 | 113.042 |
| retract_1 | retract | 0.00 / step_budget | (0.503, -0.110, 0.026)→(0.498, -0.008, 0.101) | (0.525, -0.139, 0.029)→(0.522, -0.136, 0.025) | 0.039→0.036 | 1.00 / 4.000 | 0.245 | 52.546 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.919
- lateral_force_integral: None
- approach_alignment: 0.557
- goal_progress: 0.725
- terminal_score: 0.725
- phase_score: 0.829
- phase_breakdown.contact_score: 0.848
- phase_breakdown.push_score: 0.821
- phase_breakdown.approach_score: 0.822

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.788
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.837
- **Median Q (composite search score)**: 0.459
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.321


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8267fcc1127ab3c529e380fe6aea430def9956719b146bd9818eb52355cb895d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `33d626702a3717cebb1eda35e1cb80c1c9d108c246efccd193577b9105813420`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52247,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14345,"push_1.push_distance":0.18204,"push_1.push_speed":0.09122,"retract_1.retract_height":0.15024,"retract_1.speed":0.02984},"optimized_scores":{"best_composite_score":0.39625,"best_fitness_score":0.70625,"best_task_score":0.8366},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1527.0,"contact_point_centroid":[0.48713,-0.04628,-8e-05],"force_p95":54.71416,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.22241,"mean_force":10.19635,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48168,-0.00097,0.01885]},{"body_a":"attachment","body_b":"push_box","contact_count":921.0,"contact_point_centroid":[0.48863,-0.00616,0.03156],"force_p95":38.22202,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.47581,"mean_force":11.3562,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48113,0.0054,0.01892]},{"body_a":"push_box","body_b":"link7","contact_count":290.0,"contact_point_centroid":[0.50462,0.041,0.05086],"force_p95":40.56042,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.33997,"mean_force":28.10383,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47617,0.06376,0.01976]},{"body_a":"attachment","body_b":"push_box","contact_count":105.0,"contact_point_centroid":[0.47907,0.0795,0.02918],"force_p95":8.07072,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.5515,"mean_force":3.47063,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47458,0.09126,0.02156]},{"body_a":"world","body_b":"push_box","contact_count":1861.0,"contact_point_centroid":[0.47956,0.05705,-1e-05],"force_p95":1.75689,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.83506,"mean_force":0.44468,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47369,0.11068,0.02457]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.49295,-0.09104,0.02537],"force_p95":1.33543,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.46137,"mean_force":0.60813,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4898,-0.07913,0.01922]},{"body_a":"world","body_b":"push_box","contact_count":3985.0,"contact_point_centroid":[0.49167,-0.11681,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32666,"mean_force":0.2466,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48793,-0.03753,0.05715]},{"body_a":"world","body_b":"push_box","contact_count":3972.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48715,0.06586,0.16416]}],"total_contact_groups":8},"final_pose_error":0.15443,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49163,-0.1168,0.02499],"final_tcp_position":[0.49001,0.00677,0.09313],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":68.22241,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47614,0.13178,0.03157],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":519.0,"n_steps_budget":600.0,"object_pos_end":[0.4812,0.05027,0.02512],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20115,"object_to_goal_dist_start":0.2095,"object_z_max":0.0252,"peak_contact_force":1.50959,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1966.0,"raw_peak_contact_force":11.5515,"tcp_end":[0.4749,0.08694,0.02102],"tcp_start":[0.47614,0.13178,0.03157],"tcp_to_object_dist_end":0.03743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4919,-0.11574,0.02504],"object_pos_start":[0.4812,0.05027,0.02512],"object_to_goal_dist_end":0.0352,"object_to_goal_dist_start":0.20115,"object_z_max":0.02671,"peak_contact_force":0.46248,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2738.0,"raw_peak_contact_force":68.22241,"tcp_end":[0.48988,-0.07898,0.01927],"tcp_start":[0.4749,0.08694,0.02102],"tcp_to_object_dist_end":0.03726,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49163,-0.1168,0.02499],"object_pos_start":[0.4919,-0.11574,0.02504],"object_to_goal_dist_end":0.03423,"object_to_goal_dist_start":0.0352,"object_z_max":0.02504,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3990.0,"raw_peak_contact_force":1.46137,"tcp_end":[0.49001,0.00677,0.09313],"tcp_start":[0.48988,-0.07898,0.01927],"tcp_to_object_dist_end":0.14113,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `021f3e69028f16fb65e79b302b37775f7324e143e034cbac30fdb04ffcd99d24`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5061,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19971,"push_1.push_distance":0.10475,"push_1.push_speed":0.08653,"retract_1.retract_height":0.13419,"retract_1.speed":0.0504},"optimized_scores":{"best_composite_score":0.47765,"best_fitness_score":0.78765,"best_task_score":0.72524},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":936.0,"contact_point_centroid":[0.55609,-0.0755,0.0543],"force_p95":114.33681,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.03532,"mean_force":78.36162,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52261,-0.05988,0.02365]},{"body_a":"world","body_b":"push_box","contact_count":1826.0,"contact_point_centroid":[0.55029,-0.1097,-0.00034],"force_p95":79.81149,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.33829,"mean_force":51.32961,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52237,-0.06106,0.02379]},{"body_a":"attachment","body_b":"push_box","contact_count":942.0,"contact_point_centroid":[0.54154,-0.06795,0.053],"force_p95":87.2772,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":92.64325,"mean_force":53.7654,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52272,-0.05947,0.02362]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.55086,-0.12614,0.05616],"force_p95":75.49675,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.01481,"mean_force":29.66717,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50774,-0.12053,0.03029]},{"body_a":"world","body_b":"push_box","contact_count":3639.0,"contact_point_centroid":[0.53661,-0.14686,-3e-05],"force_p95":0.34788,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":77.10013,"mean_force":0.45645,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50327,-0.07123,0.06748]},{"body_a":"attachment","body_b":"push_box","contact_count":68.0,"contact_point_centroid":[0.53039,-0.12296,0.06136],"force_p95":53.67035,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.5352,"mean_force":15.61173,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50687,-0.11776,0.03181]},{"body_a":"attachment","body_b":"push_box","contact_count":85.0,"contact_point_centroid":[0.54513,-0.00428,0.03662],"force_p95":9.6618,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.54545,"mean_force":3.39524,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.539,0.00761,0.02053]},{"body_a":"world","body_b":"push_box","contact_count":1922.0,"contact_point_centroid":[0.54452,-0.02698,-1e-05],"force_p95":0.97284,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.79059,"mean_force":0.40074,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53668,0.02975,0.024]},{"body_a":"world","body_b":"push_box","contact_count":3616.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51809,0.02558,0.16513]}],"total_contact_groups":9},"final_pose_error":0.18315,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53615,-0.14667,0.02499],"final_tcp_position":[0.50197,-0.02565,0.09815],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":134.03532,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3616.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53817,0.05149,0.03197],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":532.0,"n_steps_budget":600.0,"object_pos_end":[0.54653,-0.03298,0.02506],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12593,"object_to_goal_dist_start":0.13211,"object_z_max":0.02511,"peak_contact_force":1.15254,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2007.0,"raw_peak_contact_force":10.54545,"tcp_end":[0.53949,0.00376,0.02003],"tcp_start":[0.53817,0.05149,0.03197],"tcp_to_object_dist_end":0.03775,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":946.0,"n_steps_budget":1000.0,"object_pos_end":[0.53798,-0.14923,0.03106],"object_pos_start":[0.54653,-0.03298,0.02506],"object_to_goal_dist_end":0.03847,"object_to_goal_dist_start":0.12593,"object_z_max":0.03107,"peak_contact_force":110.01325,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3704.0,"raw_peak_contact_force":134.03532,"tcp_end":[0.50875,-0.12276,0.02895],"tcp_start":[0.53949,0.00376,0.02003],"tcp_to_object_dist_end":0.03949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53615,-0.14667,0.02499],"object_pos_start":[0.53798,-0.14923,0.03106],"object_to_goal_dist_end":0.0363,"object_to_goal_dist_start":0.03847,"object_z_max":0.03426,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3751.0,"raw_peak_contact_force":83.01481,"tcp_end":[0.50197,-0.02565,0.09815],"tcp_start":[0.50875,-0.12276,0.02895],"tcp_to_object_dist_end":0.14549,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `886824c4c8b8334954c1de9b3100fb0acfdd4a04855e7e82a07b72c52723cc86`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78767,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.28953,"push_1.push_distance":0.10232,"push_1.push_speed":0.09997,"retract_1.retract_height":0.12398,"retract_1.speed":0.08661},"optimized_scores":{"best_composite_score":0.45913,"best_fitness_score":0.76913,"best_task_score":0.70338},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":823.0,"contact_point_centroid":[0.56394,-0.08052,0.05428],"force_p95":125.40536,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":136.86739,"mean_force":84.59467,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52858,-0.06704,0.02402]},{"body_a":"world","body_b":"push_box","contact_count":1654.0,"contact_point_centroid":[0.55867,-0.11236,-0.00036],"force_p95":94.38953,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.83928,"mean_force":53.72273,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52871,-0.06667,0.024]},{"body_a":"attachment","body_b":"push_box","contact_count":824.0,"contact_point_centroid":[0.54747,-0.075,0.05402],"force_p95":81.51197,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.71949,"mean_force":53.31022,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52863,-0.06692,0.02402]},{"body_a":"world","body_b":"push_box","contact_count":3687.0,"contact_point_centroid":[0.53782,-0.14348,-2e-05],"force_p95":0.25131,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.16232,"mean_force":0.39617,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5041,-0.06405,0.07562]},{"body_a":"push_box","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.55254,-0.12985,0.05663],"force_p95":63.76895,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.9701,"mean_force":20.50863,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5091,-0.12654,0.03065]},{"body_a":"attachment","body_b":"push_box","contact_count":66.0,"contact_point_centroid":[0.53114,-0.12632,0.05961],"force_p95":34.68595,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.73242,"mean_force":9.67751,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50798,-0.12245,0.03302]},{"body_a":"attachment","body_b":"push_box","contact_count":78.0,"contact_point_centroid":[0.5553,-0.01348,0.03762],"force_p95":10.16049,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.52698,"mean_force":3.73071,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54914,-0.00161,0.02033]},{"body_a":"world","body_b":"push_box","contact_count":1978.0,"contact_point_centroid":[0.55472,-0.03622,-1e-05],"force_p95":1.02306,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.75611,"mean_force":0.39846,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54659,0.02074,0.02373]},{"body_a":"world","body_b":"push_box","contact_count":3644.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52296,0.02111,0.16506]}],"total_contact_groups":9},"final_pose_error":0.16049,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53719,-0.1435,0.02499],"final_tcp_position":[0.50216,-0.00555,0.11054],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":136.86739,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":911.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3644.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54794,0.04249,0.03178],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.55769,-0.04237,0.02486],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12211,"object_to_goal_dist_start":0.12728,"object_z_max":0.02513,"peak_contact_force":7.50497,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2056.0,"raw_peak_contact_force":15.52698,"tcp_end":[0.5497,-0.00564,0.01983],"tcp_start":[0.54794,0.04249,0.03178],"tcp_to_object_dist_end":0.03793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":836.0,"n_steps_budget":930.0,"object_pos_end":[0.54371,-0.15111,0.03103],"object_pos_start":[0.55769,-0.04237,0.02486],"object_to_goal_dist_end":0.04414,"object_to_goal_dist_start":0.12211,"object_z_max":0.03106,"peak_contact_force":122.4971,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3301.0,"raw_peak_contact_force":136.86739,"tcp_end":[0.51022,-0.12856,0.02948],"tcp_start":[0.5497,-0.00564,0.01983],"tcp_to_object_dist_end":0.04041,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53719,-0.1435,0.02499],"object_pos_start":[0.54371,-0.15111,0.03103],"object_to_goal_dist_end":0.03775,"object_to_goal_dist_start":0.04414,"object_z_max":0.03373,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3790.0,"raw_peak_contact_force":73.16232,"tcp_end":[0.50216,-0.00555,0.11054],"tcp_start":[0.51022,-0.12856,0.02948],"tcp_to_object_dist_end":0.16607,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```