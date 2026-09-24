## Search State

- **Seed**: 1
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6800 | 0.76 | ❌ rejected |
| 13 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7750 | 0.86 | ❌ rejected |
| 12 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6076 | 0.87 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6961 | 0.89 | ✅ accepted |
| 10 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6964 | 0.86 | ❌ rejected |

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

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.08, 0.00) | distance | — |
| contact | object | (0.00, 0.03, 0.00) | distance | — |
| push | goal | (0.00, 0.03, 0.00) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.680) — your mutation base

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

- **Composite score**: 0.680
- **task_score** (E): 0.764
- **fitness_score**: 0.690  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2172 |
| contact_1 | 1.00 | 1.00 | 0.0791 |
| push_1 | 0.67 | 1.00 | 0.1630 |
| retract_1 | 0.00 | 1.00 | 0.0918 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.473, 0.075, 0.102) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.473, 0.075, 0.102)→(0.470, 0.036, 0.033) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 5.000 | 21.638 | 0.245 |
| push_1 | push | 0.67 / step_budget | (0.470, 0.036, 0.033)→(0.498, -0.121, 0.021) | (0.474, -0.001, 0.025)→(0.511, -0.140, 0.027) | 0.154→0.040 | 1.00 / 2.333 | 4.175 | 31.174 |
| retract_1 | retract | 0.00 / step_budget | (0.498, -0.121, 0.021)→(0.495, -0.121, 0.113) | (0.511, -0.140, 0.027)→(0.509, -0.141, 0.025) | 0.040→0.039 | 1.00 / 4.000 | 0.245 | 3.750 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.777
- goal_progress: 0.822
- terminal_score: 0.822
- phase_score: 0.692
- phase_breakdown.push_score: 0.819
- phase_breakdown.contact_score: 0.758
- phase_breakdown.approach_score: 0.275

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.744
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.825
- **Median Q (composite search score)**: 0.711
- **K-run variance**: 0.0037
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.455


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91011,"average_solve_count":267.0,"average_success_count":267.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05041,"contact_1.speed":0.03879,"push_1.push_distance":0.10236,"retract_1.speed":0.01816},"optimized_scores":{"best_composite_score":0.59553,"best_fitness_score":0.60553,"best_task_score":0.64499},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":782.0,"contact_point_centroid":[0.50496,-0.01296,0.0462],"force_p95":17.8055,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.24844,"mean_force":5.00473,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49388,-0.00424,0.02445]},{"body_a":"push_box","body_b":"link7","contact_count":153.0,"contact_point_centroid":[0.5283,-0.04622,0.05691],"force_p95":16.06498,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.16863,"mean_force":9.21803,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49427,-0.06101,0.02337]},{"body_a":"world","body_b":"push_box","contact_count":1357.0,"contact_point_centroid":[0.53384,-0.04657,-6e-05],"force_p95":12.85897,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.64616,"mean_force":4.41018,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49399,-0.01346,0.02432]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52854,-0.08169,0.0559],"force_p95":6.16209,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.16209,"mean_force":6.16209,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49435,-0.09809,0.02243]},{"body_a":"world","body_b":"push_box","contact_count":3608.0,"contact_point_centroid":[0.53383,-0.0848,-1e-05],"force_p95":0.43258,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.65473,"mean_force":0.26904,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49077,-0.09752,0.07398]},{"body_a":"attachment","body_b":"push_box","contact_count":125.0,"contact_point_centroid":[0.50867,-0.09867,0.05339],"force_p95":0.63287,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.70993,"mean_force":0.50995,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49128,-0.09775,0.0315]},{"body_a":"world","body_b":"push_box","contact_count":3440.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49804,0.06331,0.18909]},{"body_a":"world","body_b":"push_box","contact_count":2044.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49583,0.10837,0.05337]}],"total_contact_groups":8},"final_pose_error":0.10433,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53113,-0.08458,0.02499],"final_tcp_position":[0.49098,-0.09753,0.11816],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":29.24543,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":860.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3440.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49783,0.12687,0.0811],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":511.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":29.24543,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2044.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49677,0.09105,0.03035],"tcp_start":[0.49783,0.12687,0.0811],"tcp_to_object_dist_end":0.03767,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53614,-0.08471,0.02903],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.07473,"object_to_goal_dist_start":0.20406,"object_z_max":0.02931,"peak_contact_force":11.44706,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2292.0,"raw_peak_contact_force":28.24844,"subtask_id":"push","tcp_end":[0.49435,-0.09809,0.02243],"tcp_start":[0.49677,0.09105,0.03035],"tcp_to_object_dist_end":0.04438,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53113,-0.08458,0.02499],"object_pos_start":[0.53614,-0.08471,0.02903],"object_to_goal_dist_end":0.07244,"object_to_goal_dist_start":0.07473,"object_z_max":0.02903,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3734.0,"raw_peak_contact_force":6.16209,"tcp_end":[0.49098,-0.09753,0.11816],"tcp_start":[0.49435,-0.09809,0.02243],"tcp_to_object_dist_end":0.10227,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83665,"average_solve_count":251.0,"average_success_count":251.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05549,"contact_1.speed":0.01976,"push_1.push_distance":0.02197,"retract_1.speed":0.09659},"optimized_scores":{"best_composite_score":0.73383,"best_fitness_score":0.74383,"best_task_score":0.82172},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":719.0,"contact_point_centroid":[0.48663,-0.07506,0.03996],"force_p95":20.74458,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.81725,"mean_force":5.28607,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48253,-0.06315,0.0238]},{"body_a":"world","body_b":"push_box","contact_count":1211.0,"contact_point_centroid":[0.48885,-0.10947,-6e-05],"force_p95":9.73117,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.25462,"mean_force":3.54899,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48121,-0.05754,0.0241]},{"body_a":"world","body_b":"push_box","contact_count":3958.0,"contact_point_centroid":[0.51083,-0.1705,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.08647,"mean_force":0.24793,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49576,-0.13297,0.06541]},{"body_a":"attachment","body_b":"push_box","contact_count":14.0,"contact_point_centroid":[0.50593,-0.14576,0.05001],"force_p95":1.15557,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.26447,"mean_force":0.58652,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4982,-0.13383,0.02091]},{"body_a":"world","body_b":"push_box","contact_count":2744.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48421,0.02572,0.19433]},{"body_a":"world","body_b":"push_box","contact_count":2396.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46715,0.03208,0.05808]}],"total_contact_groups":6},"final_pose_error":0.10997,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51091,-0.17025,0.02499],"final_tcp_position":[0.49592,-0.13299,0.1104],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":32.81725,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":686.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2744.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46985,0.0521,0.08948],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":599.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":23.15323,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2396.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.46735,0.01277,0.03079],"tcp_start":[0.46985,0.0521,0.08948],"tcp_to_object_dist_end":0.03762,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":879.0,"n_steps_budget":990.0,"object_pos_end":[0.51058,-0.16997,0.02546],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.02261,"object_to_goal_dist_start":0.12903,"object_z_max":0.02577,"peak_contact_force":0.1576,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1930.0,"raw_peak_contact_force":32.81725,"subtask_id":"push","tcp_end":[0.49936,-0.13377,0.02032],"tcp_start":[0.46735,0.01277,0.03079],"tcp_to_object_dist_end":0.03825,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51091,-0.17025,0.02499],"object_pos_start":[0.51058,-0.16997,0.02546],"object_to_goal_dist_end":0.023,"object_to_goal_dist_start":0.02261,"object_z_max":0.02546,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3972.0,"raw_peak_contact_force":2.08647,"tcp_end":[0.49592,-0.13299,0.1104],"tcp_start":[0.49936,-0.13377,0.02032],"tcp_to_object_dist_end":0.09438,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.85892,"average_solve_count":241.0,"average_success_count":241.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10074,"contact_1.speed":0.04117,"push_1.push_distance":0.02133,"retract_1.speed":0.0744},"optimized_scores":{"best_composite_score":0.71066,"best_fitness_score":0.72066,"best_task_score":0.82546},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":672.0,"contact_point_centroid":[0.47415,-0.07582,0.03356],"force_p95":21.91136,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.45558,"mean_force":6.61833,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47318,-0.06393,0.02781]},{"body_a":"world","body_b":"push_box","contact_count":1638.0,"contact_point_centroid":[0.47432,-0.11108,-7e-05],"force_p95":10.09513,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.69285,"mean_force":3.0411,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47519,-0.06873,0.02733]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49827,-0.14378,0.02139],"force_p95":3.00099,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.00099,"mean_force":3.00099,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50178,-0.13236,0.02062]},{"body_a":"world","body_b":"push_box","contact_count":3983.0,"contact_point_centroid":[0.48524,-0.16691,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.47986,"mean_force":0.24696,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49818,-0.13158,0.06519]},{"body_a":"world","body_b":"push_box","contact_count":2200.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47521,0.02177,0.21751]},{"body_a":"world","body_b":"push_box","contact_count":3064.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44759,0.0249,0.08486]}],"total_contact_groups":6},"final_pose_error":0.11059,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48521,-0.16685,0.02499],"final_tcp_position":[0.49834,-0.13159,0.11008],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":32.45558,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":550.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2200.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.45107,0.04453,0.13476],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":766.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":12.51568,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3064.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.44681,0.00541,0.03812],"tcp_start":[0.45107,0.04453,0.13476],"tcp_to_object_dist_end":0.03941,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":884.0,"n_steps_budget":990.0,"object_pos_end":[0.48568,-0.16597,0.02505],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.02145,"object_to_goal_dist_start":0.12843,"object_z_max":0.02568,"peak_contact_force":0.92178,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2310.0,"raw_peak_contact_force":32.45558,"subtask_id":"push","tcp_end":[0.50178,-0.13236,0.02062],"tcp_start":[0.44681,0.00541,0.03812],"tcp_to_object_dist_end":0.03753,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48521,-0.16685,0.02499],"object_pos_start":[0.48568,-0.16597,0.02505],"object_to_goal_dist_end":0.02242,"object_to_goal_dist_start":0.02145,"object_z_max":0.02506,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3984.0,"raw_peak_contact_force":3.00099,"tcp_end":[0.49834,-0.13159,0.11008],"tcp_start":[0.50178,-0.13236,0.02062],"tcp_to_object_dist_end":0.09304,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```